import argparse
import logging
import re
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
from flask import Flask, jsonify, request
from qwen_asr import Qwen3ASRModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("chunk.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# ============== RMS VAD 配置 ==============
DEFAULT_CHUNK_SIZE_SEC = 0.5  # 每个切片 500ms（与 test_streaming.py 默认值匹配）
DEFAULT_RMS_THRESHOLD = 0.02  # 声音检测能量阈值
DEFAULT_SILENCE_MS_TO_FINALIZE = 800  # 触发断句的静音时长（与 Gradio UI 默认值匹配）


@dataclass
class Session:
    """
    带 RMS VAD 状态的流式会话。

    属性:
        state: init_streaming_state() 返回的 ASR 流式状态
        created_at: 会话创建时间戳
        last_seen: 最后活动时间戳

        # VAD 状态
        in_speech: 当前是否处于语音状态
        silence_ms: 累计静音时长（毫秒）
        was_in_speech: 上一个 in_speech 状态（用于检测语音开始）

        # 句子累积
        finalized_segments: 已断句的句子列表
        last_finalized_text: 上次断句时的完整文本（用于检测新内容）
        last_vad_state_text: 上次 VAD 状态更新时的文本（用于检测变化）
    """
    state: object
    created_at: float
    last_seen: float
    language: Optional[str] = None

    # VAD 状态
    in_speech: bool = False
    silence_ms: float = 0.0
    was_in_speech: bool = False

    # 句子累积
    finalized_segments: List[str] = field(default_factory=list)
    last_finalized_text: str = ""
    last_vad_state_text: str = ""

    # 句子耗时追踪
    speech_start_time: Optional[float] = None


app = Flask(__name__)

global_asr: Optional[Qwen3ASRModel] = None
_asr_lock = threading.Lock()  # vLLM 不是线程安全的，并发调用 generate 会导致结果串流
UNFIXED_CHUNK_NUM: int = 2
UNFIXED_TOKEN_NUM: int = 5
CHUNK_SIZE_SEC: float = DEFAULT_CHUNK_SIZE_SEC
RMS_THRESHOLD: float = DEFAULT_RMS_THRESHOLD
SILENCE_MS_TO_FINALIZE: float = DEFAULT_SILENCE_MS_TO_FINALIZE

SESSIONS: Dict[str, Session] = {}
SESSION_TTL_SEC = 20 * 10 * 60  # 会话最大生命周期
NO_AUDIO_TIMEOUT_SEC = 30  # 10 秒未收到语音包则自动结束
GC_INTERVAL_SEC = 5  # 后台垃圾回收线程的检查间隔


def _gc_session_monitor():
    """后台线程：定期执行会话垃圾回收"""
    while True:
        time.sleep(GC_INTERVAL_SEC)
        try:
            _gc_sessions()
        except Exception as e:
            logger.error(f"[GC监控] 异常: {e}")


def _start_gc_monitor():
    """启动后台 GC 监控线程"""
    t = threading.Thread(target=_gc_session_monitor, daemon=True, name="gc-monitor")
    t.start()
    logger.info("[GC监控] 后台线程已启动，检查间隔=%ds", GC_INTERVAL_SEC)


def _gc_sessions():
    """
    垃圾回收过期的会话。

    两种过期类型:
    1. NO_AUDIO_TIMEOUT_SEC (3 秒): 未收到语音包 -> 自动结束并移除
    2. SESSION_TTL_SEC (200 分钟): 会话最大生命周期 -> 强制清理
    """
    now = time.time()

    # 自动结束超过 3 秒未收到语音的会话
    audio_timeout = [
        sid for sid, s in SESSIONS.items()
        if now - s.last_seen > NO_AUDIO_TIMEOUT_SEC
    ]
    for sid in audio_timeout:
        try:
            logger.info("[自动结束] 会话 %s: %.1f秒 未收到语音", sid, now - SESSIONS[sid].last_seen)
            with _asr_lock:
                global_asr.finish_streaming_transcribe(SESSIONS[sid].state)
        except Exception as e:
            logger.error("[自动结束错误] 会话 %s: %s", sid, e)
        SESSIONS.pop(sid, None)

    # 强制清理超过 SESSION_TTL_SEC 的会话
    dead = [
        sid for sid, s in SESSIONS.items()
        if now - s.last_seen > SESSION_TTL_SEC
    ]
    for sid in dead:
        try:
            with _asr_lock:
                global_asr.finish_streaming_transcribe(SESSIONS[sid].state)
        except Exception:
            pass
        SESSIONS.pop(sid, None)


def _get_session(session_id: str, update_last_seen: bool = True) -> Optional[Session]:
    """
    获取现有会话，不存在则返回 None。

    参数:
        session_id: 会话ID
        update_last_seen: 是否更新 last_seen 时间戳（默认True）
    """
    s = SESSIONS.get(session_id)
    if s and update_last_seen:
        s.last_seen = time.time()
    return s


def _calculate_rms(audio_chunk: np.ndarray) -> float:
    """
    计算音频切片的 RMS（均方根）能量。

    RMS = sqrt(mean(samples²))

    RMS 越高 = 声音越大/越活跃
    RMS 越低 = 越安静/静音
    """
    if len(audio_chunk) == 0:
        return 0.0
    return np.sqrt(np.mean(audio_chunk ** 2))


def _process_vad_and_asr(
    session: Session,
    audio_chunk: np.ndarray,
) -> Tuple[bool, Optional[str], bool, bool, int]:
    """
    使用 RMS VAD 和流式 ASR 处理音频切片。

    返回:
        (is_speech, finalized_sentence, is_start, is_end, segment_index)
        - is_speech: 此切片是否包含语音
        - finalized_sentence: 如果 VAD 触发断句则返回完成的句子，否则为 None
        - is_start: 此切片是否标记语音开始
        - is_end: 此切片是否标记句子结束（断句）
        - segment_index: 断句索引（第n个断句，从0开始）
    """
    global RMS_THRESHOLD, SILENCE_MS_TO_FINALIZE

    # 计算 VAD 的 RMS 值
    rms = _calculate_rms(audio_chunk)

    # 根据音频长度计算实际切片时长（16kHz 采样率）
    actual_chunk_ms = (len(audio_chunk) / 16000) * 1000

    is_speech = rms > RMS_THRESHOLD

    # 检测语音开始（从非语音到语音的转换）
    is_start = is_speech and not session.was_in_speech

    # 更新 VAD 状态机
    if is_speech:
        session.in_speech = True
        session.silence_ms = 0
    else:
        if session.in_speech:
            # 根据实际切片时长累加静音时间
            session.silence_ms += actual_chunk_ms

    # 从 ASR 状态获取当前文本
    current_text = session.state.text.strip()

    # 检查是否应该断句（语音后的静音 + 有新文本）
    finalized_sentence = None
    is_end = False
    if session.in_speech and session.silence_ms >= SILENCE_MS_TO_FINALIZE:
        # 触发断句 - 提取自上次断句以来的新文本
        if len(current_text) > len(session.last_finalized_text):
            new_text = current_text[len(session.last_finalized_text):]
            if new_text.strip():
                finalized_sentence = new_text.strip()
                session.finalized_segments.append(finalized_sentence)
                session.last_finalized_text = current_text
                is_end = True  # 标记此切片为句子结束

        # 重置 VAD 状态以处理下一句
        session.in_speech = False
        session.silence_ms = 0

        # 断句后重置 ASR state，防止 audio_accum 无限增长导致推理越来越慢
        if is_end:
            session.state = global_asr.init_streaming_state(
                unfixed_chunk_num=UNFIXED_CHUNK_NUM,
                unfixed_token_num=UNFIXED_TOKEN_NUM,
                chunk_size_sec=CHUNK_SIZE_SEC,
                language=session.language,
            )
            session.last_finalized_text = ""

    # 保存上一次状态供下一次迭代使用（用原始 is_speech，而非状态机的 in_speech）
    session.was_in_speech = is_speech

    # 流式 ASR: 加锁保护 vLLM 推理，防止并发请求结果串流
    with _asr_lock:
        global_asr.streaming_transcribe(audio_chunk, session.state)

    return is_speech, finalized_sentence, is_start, is_end, len(session.finalized_segments) - 1 if is_end and finalized_sentence else len(session.finalized_segments)




@app.post("/api/start")
def api_start():
    session_id = uuid.uuid4().hex
    language = request.args.get("language", "Chinese")
    state = global_asr.init_streaming_state(
        unfixed_chunk_num=UNFIXED_CHUNK_NUM,
        unfixed_token_num=UNFIXED_TOKEN_NUM,
        chunk_size_sec=CHUNK_SIZE_SEC,
        language=language,
    )
    now = time.time()
    SESSIONS[session_id] = Session(state=state, created_at=now, last_seen=now, language=language)
    logger.info("[start] time=%s session_id=%s", time.strftime("%Y-%m-%d %H:%M:%S"), session_id)
    return jsonify({"session_id": session_id})


@app.post("/api/chunk")
def api_chunk():
    t0 = time.time()
    session_id = request.args.get("session_id", "")
    seq_type = request.args.get("seq_type", 1, type=int)
    s = _get_session(session_id)
    if not s:
        return jsonify({"error": "invalid session_id"}), 400

    if request.mimetype != "application/octet-stream":
        return jsonify({"error": "expect application/octet-stream"}), 400

    raw = request.get_data(cache=False)
    if len(raw) % 4 != 0:
        return jsonify({"error": "float32 bytes length not multiple of 4"}), 400

    wav = np.frombuffer(raw, dtype=np.float32).reshape(-1)

    # 使用 VAD 和 ASR 处理
    is_speech, finalized, is_start, is_end, segment_index = _process_vad_and_asr(s, wav)

    # seq_type=0：首包，is_start 强制为 True
    if seq_type == 0:
        is_start = True

    # seq_type=2：尾包，is_end 强制为 True
    if seq_type == 2:
        is_end = True

    # 记录语音开始时间
    if is_start:
        s.speech_start_time = t0

    # 获取完整文本和新文本（自上次断句以来的内容）
    full_text = getattr(s.state, "text", "") or ""
    new_text = full_text[len(s.last_finalized_text):] if full_text else ""

    # 当 is_end 时，返回刚断句的文本而非静音chunk的空文本
    if is_end and s.finalized_segments:
        new_text = s.finalized_segments[-1]

    response_data = {
        "language": getattr(s.state, "language", "") or "",
        "text": new_text,
        "full_text": full_text,
        "finalized_segments": list(s.finalized_segments),
        "vad_status": {
            "is_speech": bool(is_speech),
            "silence_ms": float(s.silence_ms),
            "is_start": bool(is_start),
            "is_end": bool(is_end),
            "segment_index": segment_index,
        }
    }

    vad = response_data["vad_status"]
    elapsed_ms = (time.time() - t0) * 1000
    perf_tag = " [严重超时]" if elapsed_ms > 400 else " [延迟]" if elapsed_ms > 200 else " [缓慢]" if elapsed_ms > 100 else ""
    logger.info(
        "[vad] time=%s session_id=%s cost=%.1fms%s | is_start=%s is_end=%s is_speech=%s silence_ms=%.1f seg=%s"
        " | lang=%s text=%r",
        time.strftime("%Y-%m-%d %H:%M:%S"), session_id, elapsed_ms, perf_tag,
        vad["is_start"], vad["is_end"], vad["is_speech"], vad["silence_ms"],
        vad["segment_index"], response_data["language"],
        response_data["text"],
    )
    if is_end and s.speech_start_time is not None:
        sentence_total_ms = (time.time() - s.speech_start_time) * 1000
        logger.info(
            "[sentence] session_id=%s seg=%s 从开始到断句总耗时=%.1fms | text=%r",
            session_id, vad["segment_index"], sentence_total_ms, response_data["text"],
        )
        s.speech_start_time = None
    return jsonify(response_data)


@app.post("/api/finish")
def api_finish():
    session_id = request.args.get("session_id", "")
    s = _get_session(session_id)
    if not s:
        return jsonify({"error": "invalid session_id"}), 400

    with _asr_lock:
        global_asr.finish_streaming_transcribe(s.state)

    # 将剩余文本添加为最终片段
    remaining = s.state.text.strip()
    last_finalized = s.last_finalized_text.strip()
    if len(remaining) > len(last_finalized):
        new_text = remaining[len(last_finalized):]
        if new_text.strip():
            s.finalized_segments.append(new_text.strip())

    out = {
        "language": getattr(s.state, "language", "") or "",
        "text": getattr(s.state, "text", "") or "",
        "finalized_segments": list(s.finalized_segments),
    }
    SESSIONS.pop(session_id, None)
    return jsonify(out)


def parse_args():
    p = argparse.ArgumentParser(description="Qwen3-ASR 流式 Web Demo，带 RMS VAD（vLLM 后端）")
    p.add_argument("--asr-model-path", default="/root/Qwen3-ASR-1.7B", help="模型名称或本地路径")
    p.add_argument("--host", default="0.0.0.0", help="绑定主机")
    p.add_argument("--port", type=int, default=8000, help="绑定端口")
    p.add_argument("--gpu-memory-utilization", type=float, default=0.5, help="vLLM GPU 显存利用率")

    p.add_argument("--unfixed-chunk-num", type=int, default=2, help="前缀之前的初始切片数量")
    p.add_argument("--unfixed-token-num", type=int, default=5, help="回滚的 token 数量")
    p.add_argument("--chunk-size-sec", type=float, default=DEFAULT_CHUNK_SIZE_SEC, help="切片时长（秒）")
    p.add_argument("--rms-threshold", type=float, default=DEFAULT_RMS_THRESHOLD, help="VAD 的 RMS 能量阈值")
    p.add_argument("--silence-ms", type=float, default=DEFAULT_SILENCE_MS_TO_FINALIZE, help="触发断句的静音时长")
    return p.parse_args()


def main():
    global args
    global global_asr
    global UNFIXED_CHUNK_NUM
    global UNFIXED_TOKEN_NUM
    global CHUNK_SIZE_SEC
    global RMS_THRESHOLD
    global SILENCE_MS_TO_FINALIZE

    args = parse_args()

    UNFIXED_CHUNK_NUM = args.unfixed_chunk_num
    UNFIXED_TOKEN_NUM = args.unfixed_token_num
    CHUNK_SIZE_SEC = args.chunk_size_sec
    RMS_THRESHOLD = args.rms_threshold
    SILENCE_MS_TO_FINALIZE = args.silence_ms

    global_asr = Qwen3ASRModel.LLM(
        model=args.asr_model_path,
        gpu_memory_utilization=args.gpu_memory_utilization,
        max_new_tokens=32,
    )
    logger.info("模型已加载：%s", args.asr_model_path)
    logger.info("VAD 设置：RMS 阈值=%.4f, 静音断句=%dms", RMS_THRESHOLD, SILENCE_MS_TO_FINALIZE)
    logger.info("服务器启动于 http://%s:%d/", args.host, args.port)
    _start_gc_monitor()
    app.run(host=args.host, port=args.port, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    main()
