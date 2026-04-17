# Graph Report - .  (2026-04-16)

## Corpus Check
- Corpus is ~21,391 words - fits in a single context window. You may not need a graph.

## Summary
- 334 nodes · 702 edges · 17 communities detected
- Extraction: 67% EXTRACTED · 33% INFERRED · 0% AMBIGUOUS · INFERRED: 233 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Configuration Classes|Configuration Classes]]
- [[_COMMUNITY_Model Architecture|Model Architecture]]
- [[_COMMUNITY_CLI and Entry Points|CLI and Entry Points]]
- [[_COMMUNITY_Streaming Inference|Streaming Inference]]
- [[_COMMUNITY_vLLM Backend|vLLM Backend]]
- [[_COMMUNITY_Transformers Backend|Transformers Backend]]
- [[_COMMUNITY_Inference Pipeline|Inference Pipeline]]
- [[_COMMUNITY_Audio Processing|Audio Processing]]
- [[_COMMUNITY_Tokenization|Tokenization]]
- [[_COMMUNITY_Forced Alignment|Forced Alignment]]
- [[_COMMUNITY_Utility Functions|Utility Functions]]
- [[_COMMUNITY_Data Structures|Data Structures]]
- [[_COMMUNITY_Speech Preprocessing|Speech Preprocessing]]
- [[_COMMUNITY_Serving API|Serving API]]
- [[_COMMUNITY_Module Exports|Module Exports]]
- [[_COMMUNITY_Model Weights|Model Weights]]
- [[_COMMUNITY_Demo Applications|Demo Applications]]

## God Nodes (most connected - your core abstractions)
1. `Qwen3ASRAudioEncoderConfig` - 65 edges
2. `Qwen3ASRThinkerConfig` - 65 edges
3. `Qwen3ASRConfig` - 65 edges
4. `Qwen3ASRProcessor` - 27 edges
5. `Qwen3ForcedAligner` - 22 edges
6. `Qwen3ASRForConditionalGeneration` - 21 edges
7. `AudioChunk` - 19 edges
8. `Qwen3ASRModel` - 16 edges
9. `Qwen3ForceAlignProcessor` - 14 edges
10. `Qwen3ASRThinkerForConditionalGeneration` - 12 edges

## Surprising Connections (you probably didn't know these)
- `Qwen3ASRTextRMSNorm` --uses--> `Qwen3ASRAudioEncoderConfig`  [INFERRED]
  qwen_asr\core\transformers_backend\modeling_qwen3_asr.py → qwen_asr\core\transformers_backend\configuration_qwen3_asr.py
- `Qwen3ASRTextAttention` --uses--> `Qwen3ASRAudioEncoderConfig`  [INFERRED]
  qwen_asr\core\transformers_backend\modeling_qwen3_asr.py → qwen_asr\core\transformers_backend\configuration_qwen3_asr.py
- `Qwen3ASRTextMLP` --uses--> `Qwen3ASRAudioEncoderConfig`  [INFERRED]
  qwen_asr\core\transformers_backend\modeling_qwen3_asr.py → qwen_asr\core\transformers_backend\configuration_qwen3_asr.py
- `Qwen3ASRThinkerTextDecoderLayer` --uses--> `Qwen3ASRAudioEncoderConfig`  [INFERRED]
  qwen_asr\core\transformers_backend\modeling_qwen3_asr.py → qwen_asr\core\transformers_backend\configuration_qwen3_asr.py
- `Qwen3ASRPreTrainedModel` --uses--> `Qwen3ASRAudioEncoderConfig`  [INFERRED]
  qwen_asr\core\transformers_backend\modeling_qwen3_asr.py → qwen_asr\core\transformers_backend\configuration_qwen3_asr.py

## Communities

### Community 0 - "Configuration Classes"
Cohesion: 0.05
Nodes (46): Qwen3ASRConfig, Qwen3ASRThinkerConfig, r"""     This is the configuration class to store the configuration of a [`Qwen, This is the configuration class to store the configuration of a [`Qwen3ASRForCon, Returns the config that is meant to be used with text IO. On most models, it is, GenerationMixin, GradientCheckpointingLayer, apply_rotary_pos_emb() (+38 more)

### Community 1 - "Model Architecture"
Cohesion: 0.1
Nodes (25): ASRStreamingState, ASRTranscription, from_pretrained(), LLM(), Qwen3ASRModel, Unified inference wrapper for Qwen3-ASR with two backends:       - Transformers, Initialize using Transformers backend.          Args:             pretrained_, Initialize using vLLM backend.          Import is isolated to keep vLLM option (+17 more)

### Community 2 - "CLI and Entry Points"
Cohesion: 0.1
Nodes (20): Qwen3ASRAudioEncoderConfig, r"""     This is the configuration class to store the configuration of a [`Qwen, Qwen3ASRProcessor, Splits token index list into chunks based on token value ranges.          Give, r"""     Constructs a Qwen3ASR processor.     [`Qwen3ASRProcessor`] offers all, Main method to prepare for the model one or several sequences(s) and audio(s). T, ProcessorMixin, Qwen3ASRAudioAttention (+12 more)

### Community 3 - "Streaming Inference"
Cohesion: 0.1
Nodes (12): BaseProcessingInfo, MultiModalDataParser, _get_feat_extract_output_lengths(), get_generation_prompt(), get_placeholder_str(), _qwen3asr_field_config(), Qwen3ASRDummyInputsBuilder, Qwen3ASRMultiModalDataParser (+4 more)

### Community 4 - "vLLM Backend"
Cohesion: 0.14
Nodes (7): align(), ForcedAlignItem, ForcedAlignResult, from_pretrained(), Qwen3ForceAlignProcessor, One aligned item span.      Attributes:         text (str):             The, Forced alignment output for one sample.      Attributes:         items (List[

### Community 5 - "Transformers Backend"
Cohesion: 0.12
Nodes (23): chunk_list(), decode_base64_bytes(), detect_and_fix_repetitions(), ensure_list(), float_range_normalize(), is_probably_base64(), is_url(), load_audio_any() (+15 more)

### Community 6 - "Inference Pipeline"
Cohesion: 0.19
Nodes (18): _apply_cuda_visible_devices(), _audio_to_tuple(), _build_choices_and_map(), build_demo(), build_parser(), _coerce_special_types(), _default_aligner_kwargs(), _default_backend_kwargs() (+10 more)

### Community 7 - "Audio Processing"
Cohesion: 0.13
Nodes (10): forward(), _get_feat_extract_output_lengths(), Qwen3ASRPreTrainedModelForConditionalGeneration, Qwen3ASRThinkerForConditionalGeneration, Encodes audios into continuous embeddings that can be forwarded to the language, Obtains multimodal placeholder mask from `input_ids` or `inputs_embeds`, and che, Computes the output length of the convolutional layers and the output length of, Creates a causal 4D mask of shape `(batch_size, 1, query_length, key_value_lengt (+2 more)

### Community 8 - "Tokenization"
Cohesion: 0.18
Nodes (15): api_chunk(), api_finish(), api_start(), _calculate_rms(), _gc_sessions(), _get_session(), main(), parse_args() (+7 more)

### Community 9 - "Forced Alignment"
Cohesion: 0.15
Nodes (6): Qwen3ASRForConditionalGeneration, Get the module prefix in multimodal models, SupportsMRoPE, SupportsMultiModal, SupportsPP, SupportsTranscription

### Community 10 - "Utility Functions"
Cohesion: 0.31
Nodes (8): api_chunk(), api_finish(), api_start(), _gc_sessions(), _get_session(), main(), parse_args(), Session

### Community 11 - "Data Structures"
Cohesion: 0.33
Nodes (3): Qwen3ASRTextConfig, r"""     This is the configuration class to store the configuration of a [`Qwen, PretrainedConfig

### Community 12 - "Speech Preprocessing"
Cohesion: 0.33
Nodes (4): _get_feat_extract_output_lengths(), Qwen3ASRProcessorKwargs, Computes the output length of the convolutional layers and the output length of, ProcessingKwargs

### Community 13 - "Serving API"
Cohesion: 1.0
Nodes (0): 

### Community 14 - "Module Exports"
Cohesion: 1.0
Nodes (0): 

### Community 15 - "Model Weights"
Cohesion: 1.0
Nodes (1): Load Qwen3-ForcedAligner model and initialize processors.          This method

### Community 16 - "Demo Applications"
Cohesion: 1.0
Nodes (1): Run forced alignment for batch or single sample.          Args:             a

## Knowledge Gaps
- **31 isolated node(s):** `带 RMS VAD 状态的流式会话。      属性:         state: init_streaming_state() 返回的 ASR 流式状`, `垃圾回收过期的会话。      两种过期类型:     1. NO_AUDIO_TIMEOUT_SEC (3 秒): 未收到语音包 -> 自动结束并移除`, `获取现有会话，不存在则返回 None。      参数:         session_id: 会话ID         update_last_se`, `计算音频切片的 RMS（均方根）能量。      RMS = sqrt(mean(samples²))      RMS 越高 = 声音越大/越活跃`, `使用 RMS VAD 和流式 ASR 处理音频切片。      返回:         (is_speech, finalized_sentence, i` (+26 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Serving API`** (2 nodes): `main()`, `__main__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module Exports`** (2 nodes): `serve.py`, `main()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Model Weights`** (1 nodes): `Load Qwen3-ForcedAligner model and initialize processors.          This method`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Demo Applications`** (1 nodes): `Run forced alignment for batch or single sample.          Args:             a`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Qwen3ASRConfig` connect `Community 0` to `Community 2`, `Community 3`, `Community 7`, `Community 9`, `Community 11`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Why does `Qwen3ASRAudioEncoderConfig` connect `Community 2` to `Community 0`, `Community 3`, `Community 7`, `Community 9`, `Community 11`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `Qwen3ASRThinkerConfig` connect `Community 0` to `Community 2`, `Community 3`, `Community 7`, `Community 9`, `Community 11`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Are the 60 inferred relationships involving `Qwen3ASRAudioEncoderConfig` (e.g. with `Qwen3ASRTextRMSNorm` and `Qwen3ASRTextAttention`) actually correct?**
  _`Qwen3ASRAudioEncoderConfig` has 60 INFERRED edges - model-reasoned connections that need verification._
- **Are the 60 inferred relationships involving `Qwen3ASRThinkerConfig` (e.g. with `Qwen3ASRTextRMSNorm` and `Qwen3ASRTextAttention`) actually correct?**
  _`Qwen3ASRThinkerConfig` has 60 INFERRED edges - model-reasoned connections that need verification._
- **Are the 60 inferred relationships involving `Qwen3ASRConfig` (e.g. with `Qwen3ASRTextRMSNorm` and `Qwen3ASRTextAttention`) actually correct?**
  _`Qwen3ASRConfig` has 60 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `Qwen3ASRProcessor` (e.g. with `SinusoidsPositionEmbedding` and `Qwen3ASRAudioAttention`) actually correct?**
  _`Qwen3ASRProcessor` has 19 INFERRED edges - model-reasoned connections that need verification._