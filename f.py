# coding=utf-8
import argparse
import time
import wave
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import requests


def load_wav_as_float32_16k(path: str) -> np.ndarray:
    with wave.open(path, "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    if sampwidth == 2:
        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    elif sampwidth == 4:
        samples = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        raise ValueError(f"不支持的采样位宽：{sampwidth}")

    if n_channels > 1:
        samples = samples.reshape(-1, n_channels).mean(axis=1)

    if framerate != 16000:
        ratio = 16000 / framerate
        out_len = max(0, round(len(samples) * ratio))
        indices = np.arange(out_len) / ratio
        idx0 = np.floor(indices).astype(int)
        idx1 = np.minimum(idx0 + 1, len(samples) - 1)
        t = indices - idx0
        samples = samples[idx0] * (1 - t) + samples[idx1] * t

    return samples.astype(np.float32)


def make_sine_wave(duration_sec: float = 3.0, freq: float = 440.0, sr: int = 16000) -> np.ndarray:
    t = np.linspace(0, duration_sec, int(sr * duration_sec), endpoint=False)
    return (np.sin(2 * np.pi * freq * t) * 0.3).astype(np.float32)


def run_streaming_test(audio: np.ndarray, base_url: str, chunk_ms: int, realtime: bool, label: str = ""):
    prefix = f"[{label}] " if label else ""
    sr = 16000
    chunk_samples = int(sr * chunk_ms / 1000)
    total_chunks = (len(audio) + chunk_samples - 1) // chunk_samples

    # 1. start
    r = requests.post(f"{base_url}/api/start", timeout=10)
    r.raise_for_status()
    session_id = r.json()["session_id"]
    print(f"{prefix}session_id={session_id}")

    # 2. chunk
    for i in range(total_chunks):
        chunk = audio[i * chunk_samples : (i + 1) * chunk_samples]

        r = requests.post(
            f"{base_url}/api/chunk",
            params={"session_id": session_id},
            headers={"Content-Type": "application/octet-stream"},
            data=chunk.tobytes(),
            timeout=30,
        )
        r.raise_for_status()

        d = r.json()
        vad = d.get("vad_status", {})
        print(f"{prefix}[vad] is_start={vad.get('is_start')} is_end={vad.get('is_end')} is_speech={vad.get('is_speech')} silence_ms={vad.get('silence_ms')} seg={vad.get('segment_index')}"
              f" | lang={d.get('language')} text={d.get('text')!r} full={d.get('full_text')!r}"
              f" | finalized={d.get('finalized_segments')}")

        if realtime:
            time.sleep(chunk_ms / 1000)

    # 3. finish
    r = requests.post(
        f"{base_url}/api/finish",
        params={"session_id": session_id},
        timeout=30,
    )
    r.raise_for_status()

    print(f"{prefix}final result: {r.json()}")
    return session_id, r.json()


def main():
    p = argparse.ArgumentParser(description="ASR 流式测试（精简版，仅打印返回）")
    p.add_argument("--url", default="http://172.23.32.85:8000/", help="服务器地址")
    p.add_argument("--audio", default="yuan.WAV")
    p.add_argument("--sine", action="store_true")
    p.add_argument("--chunk-ms", type=int, default=500)
    p.add_argument("--realtime", action="store_true")
    p.add_argument("--concurrent", action="store_true", help="并发识别 yuan.WAV 和 yuan2.WAV")
    args = p.parse_args()

    base_url = args.url.rstrip("/")

    if args.concurrent:
        # 并发模式：同时识别 yuan.WAV 和 yuan2.WAV
        audio_files = [("yuan.WAV", "A"), ("yuan2.WAV", "B")]
        audios = []
        for path, label in audio_files:
            audio = load_wav_as_float32_16k(path)
            audios.append((audio, label))

        print(f"开始并发识别: {[label for _, label in audios]}")
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {}
            for audio, label in audios:
                future = executor.submit(run_streaming_test, audio, base_url, args.chunk_ms, args.realtime, label)
                futures[future] = label

            for future in as_completed(futures):
                label = futures[future]
                try:
                    session_id, result = future.result()
                    print(f"[{label}] 完成，session_id={session_id}")
                except Exception as e:
                    print(f"[{label}] 出错: {e}")
        print("所有并发任务完成")
    else:
        if args.audio:
            audio = load_wav_as_float32_16k(args.audio)
        elif args.sine:
            audio = make_sine_wave(duration_sec=3.0)
        else:
            p.error("请提供 --audio 或 --sine")

        run_streaming_test(audio, base_url, args.chunk_ms, args.realtime)


if __name__ == "__main__":
    main()