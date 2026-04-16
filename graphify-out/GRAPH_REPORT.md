# Graph Report - .  (2026-04-14)

## Corpus Check
- Corpus is ~27,617 words - fits in a single context window. You may not need a graph.

## Summary
- 411 nodes ¡¤ 827 edges ¡¤ 25 communities detected
- Extraction: 71% EXTRACTED ¡¤ 29% INFERRED ¡¤ 0% AMBIGUOUS ¡¤ INFERRED: 238 edges (avg confidence: 0.51)
- Token cost: 8,500 input ¡¤ 1,200 output

## Community Hubs (Navigation)
- [[_COMMUNITY_ASR Model Core API|ASR Model Core API]]
- [[_COMMUNITY_Inference Engine Internals|Inference Engine Internals]]
- [[_COMMUNITY_Audio Processor|Audio Processor]]
- [[_COMMUNITY_Fine-Tuning Pipeline|Fine-Tuning Pipeline]]
- [[_COMMUNITY_Audio Encoder Architecture|Audio Encoder Architecture]]
- [[_COMMUNITY_Inference Utilities|Inference Utilities]]
- [[_COMMUNITY_Forced Aligner Examples|Forced Aligner Examples]]
- [[_COMMUNITY_Gradio Web Demo|Gradio Web Demo]]
- [[_COMMUNITY_SFT Training Script|SFT Training Script]]
- [[_COMMUNITY_Model Configuration|Model Configuration]]
- [[_COMMUNITY_Config and Attention|Config and Attention]]
- [[_COMMUNITY_Rotary Embeddings and MLP|Rotary Embeddings and MLP]]
- [[_COMMUNITY_Forced Aligner Core|Forced Aligner Core]]
- [[_COMMUNITY_Audio Encoder Module|Audio Encoder Module]]
- [[_COMMUNITY_Pretrained Model Base|Pretrained Model Base]]
- [[_COMMUNITY_Thinker Conditional Generation|Thinker Conditional Generation]]
- [[_COMMUNITY_Transformers Backend Examples|Transformers Backend Examples]]
- [[_COMMUNITY_vLLM Backend Examples|vLLM Backend Examples]]
- [[_COMMUNITY_Streaming Demo Server|Streaming Demo Server]]
- [[_COMMUNITY_vLLM Streaming Examples|vLLM Streaming Examples]]
- [[_COMMUNITY_Rotary Position Embedding|Rotary Position Embedding]]
- [[_COMMUNITY_CLI Entry Point|CLI Entry Point]]
- [[_COMMUNITY_vLLM Serve CLI|vLLM Serve CLI]]
- [[_COMMUNITY_Aligner Rationale|Aligner Rationale]]
- [[_COMMUNITY_Aligner Rationale|Aligner Rationale]]

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
  qwen_asr\core\transformers_backend\modeling_qwen3_asr.py ¡ú qwen_asr\core\transformers_backend\configuration_qwen3_asr.py
- `Qwen3ASRTextAttention` --uses--> `Qwen3ASRAudioEncoderConfig`  [INFERRED]
  qwen_asr\core\transformers_backend\modeling_qwen3_asr.py ¡ú qwen_asr\core\transformers_backend\configuration_qwen3_asr.py
- `Qwen3ASRTextMLP` --uses--> `Qwen3ASRAudioEncoderConfig`  [INFERRED]
  qwen_asr\core\transformers_backend\modeling_qwen3_asr.py ¡ú qwen_asr\core\transformers_backend\configuration_qwen3_asr.py
- `Qwen3ASRThinkerTextDecoderLayer` --uses--> `Qwen3ASRAudioEncoderConfig`  [INFERRED]
  qwen_asr\core\transformers_backend\modeling_qwen3_asr.py ¡ú qwen_asr\core\transformers_backend\configuration_qwen3_asr.py
- `Qwen3ASRPreTrainedModel` --uses--> `Qwen3ASRAudioEncoderConfig`  [INFERRED]
  qwen_asr\core\transformers_backend\modeling_qwen3_asr.py ¡ú qwen_asr\core\transformers_backend\configuration_qwen3_asr.py

## Hyperedges (group relationships)
- **Qwen3-ASR Model Family** ¡ª readme_qwen3_asr_1_7b, readme_qwen3_asr_0_6b, readme_qwen3_forced_aligner [EXTRACTED 0.95]
- **Inference Backend Options** ¡ª readme_transformers_backend, readme_vllm_backend, readme_streaming_inference, readme_offline_inference [EXTRACTED 0.90]

## Communities

### Community 0 - "ASR Model Core API"
Cohesion: 0.07
Nodes (30): ASRStreamingState, ASRTranscription, from_pretrained(), LLM(), Qwen3ASRModel, Unified inference wrapper for Qwen3-ASR with two backends:       - Transformers, Initialize using Transformers backend.          Args:             pretrained_, Initialize using vLLM backend.          Import is isolated to keep vLLM option (+22 more)

### Community 1 - "Inference Engine Internals"
Cohesion: 0.06
Nodes (18): BaseProcessingInfo, MultiModalDataParser, _get_feat_extract_output_lengths(), get_generation_prompt(), get_placeholder_str(), _qwen3asr_field_config(), Qwen3ASRDummyInputsBuilder, Qwen3ASRForConditionalGeneration (+10 more)

### Community 2 - "Audio Processor"
Cohesion: 0.07
Nodes (20): _get_feat_extract_output_lengths(), Qwen3ASRProcessor, Qwen3ASRProcessorKwargs, Splits token index list into chunks based on token value ranges.          Give, Computes the output length of the convolutional layers and the output length of, r"""     Constructs a Qwen3ASR processor.     [`Qwen3ASRProcessor`] offers all, Main method to prepare for the model one or several sequences(s) and audio(s). T, ProcessingKwargs (+12 more)

### Community 3 - "Fine-Tuning Pipeline"
Cohesion: 0.08
Nodes (28): JSONL Audio-Text Training Format, Language Prefix in Training Data, Rationale: NAR Architecture for Forced Alignment, Rationale: Unified Offline/Streaming Model Design, Supervised Fine-Tuning (SFT), Multi-GPU Training (torchrun), 52 Languages and Dialects Support, DashScope API (+20 more)

### Community 4 - "Audio Encoder Architecture"
Cohesion: 0.1
Nodes (11): GradientCheckpointingLayer, Qwen3ASRAudioEncoderLayer, Qwen3ASRTextAttention, Qwen3ASRTextMLP, Qwen3ASRTextRMSNorm, Qwen3ASRThinkerTextDecoderLayer, Qwen3ASRThinkerTextModel, Multi-headed attention from 'Attention Is All You Need' paper (+3 more)

### Community 5 - "Inference Utilities"
Cohesion: 0.12
Nodes (23): chunk_list(), decode_base64_bytes(), detect_and_fix_repetitions(), ensure_list(), float_range_normalize(), is_probably_base64(), is_url(), load_audio_any() (+15 more)

### Community 6 - "Forced Aligner Examples"
Cohesion: 0.19
Nodes (19): _download_audio_bytes(), main(), _print_result(), Single-sample alignment using HTTPS URL audio input., Batch alignment using HTTPS URL audio input., Single-sample alignment using base64 data URL audio input., Single-sample alignment using (np.ndarray, sr) input where waveform is obtained, Batch alignment mixing URL, base64, and (np.ndarray, sr) inputs. (+11 more)

### Community 7 - "Gradio Web Demo"
Cohesion: 0.19
Nodes (18): _apply_cuda_visible_devices(), _audio_to_tuple(), _build_choices_and_map(), build_demo(), build_parser(), _coerce_special_types(), _default_aligner_kwargs(), _default_backend_kwargs() (+10 more)

### Community 8 - "SFT Training Script"
Cohesion: 0.17
Nodes (12): CastFloatInputsTrainer, copy_required_hf_files_for_qwen_asr(), DataCollatorForQwen3ASRFinetuning, find_latest_checkpoint(), load_audio(), main(), make_preprocess_fn_prefix_only(), MakeEveryCheckpointInferableCallback (+4 more)

### Community 9 - "Model Configuration"
Cohesion: 0.17
Nodes (9): Qwen3ASRTextConfig, Qwen3ASRThinkerConfig, r"""     This is the configuration class to store the configuration of a [`Qwen, r"""     This is the configuration class to store the configuration of a [`Qwen, Qwen3ASRThinkerTextAttention, Qwen3ASRThinkerTextRMSNorm, Qwen3ASRThinkerTextRMSNorm is equivalent to T5LayerNorm, Multi-headed attention from 'Attention Is All You Need' paper (+1 more)

### Community 10 - "Config and Attention"
Cohesion: 0.16
Nodes (12): Qwen3ASRConfig, This is the configuration class to store the configuration of a [`Qwen3ASRForCon, Returns the config that is meant to be used with text IO. On most models, it is, Qwen3ASRAudioAttention, Qwen3ASRThinkerCausalLMOutputWithPast, r"""         feature_attention_mask (`torch.Tensor` of shape `(batch_size, feat, r"""     Args:         rope_deltas (`torch.LongTensor` of shape `(batch_size,, Multi-headed attention from 'Attention Is All You Need' paper (+4 more)

### Community 11 - "Rotary Embeddings and MLP"
Cohesion: 0.16
Nodes (9): apply_rotary_pos_emb(), eager_attention_forward(), Qwen3ASRThinkerTextMLP, Applies Rotary Position Embedding to the query and key tensors.      Args:, # NOTE: the created attention masl only approximates the ragged FA2 attention by, Rotates half the hidden dims of the input., This is the equivalent of torch.repeat_interleave(x, dim=1, repeats=n_rep). The, repeat_kv() (+1 more)

### Community 12 - "Forced Aligner Core"
Cohesion: 0.29
Nodes (2): align(), Qwen3ForceAlignProcessor

### Community 13 - "Audio Encoder Module"
Cohesion: 0.15
Nodes (7): GenerationMixin, Qwen3ASRAudioEncoder, Qwen3ASRForConditionalGeneration, Qwen3ASRPreTrainedModel, Qwen3ASRThinkerTextPreTrainedModel, Pads a sequence of tensors to their maximum length on indicated `padding_side`., PreTrainedModel

### Community 14 - "Pretrained Model Base"
Cohesion: 0.24
Nodes (7): Qwen3ASRAudioEncoderConfig, r"""     This is the configuration class to store the configuration of a [`Qwen, Qwen3ASRPreTrainedModelForConditionalGeneration, Creates a causal 4D mask of shape `(batch_size, 1, query_length, key_value_lengt, Splits token index list into chunks based on token value ranges.          Give, Calculate the rope index in LLM.          Explanation:             Each embed, r"""         feature_lens (`torch.LongTensor` of shape `(batch_size,)`):

### Community 15 - "Thinker Conditional Generation"
Cohesion: 0.24
Nodes (6): forward(), _get_feat_extract_output_lengths(), Qwen3ASRThinkerForConditionalGeneration, Encodes audios into continuous embeddings that can be forwarded to the language, Obtains multimodal placeholder mask from `input_ids` or `inputs_embeds`, and che, Computes the output length of the convolutional layers and the output length of

### Community 16 - "Transformers Backend Examples"
Cohesion: 0.49
Nodes (9): _download_audio_bytes(), main(), _print_result(), _read_wav_from_bytes(), test_batch_mixed(), test_batch_with_timestamps(), test_single_url(), test_single_with_timestamps() (+1 more)

### Community 17 - "vLLM Backend Examples"
Cohesion: 0.49
Nodes (9): _download_audio_bytes(), main(), _print_result(), _read_wav_from_bytes(), test_batch_mixed(), test_batch_with_timestamps(), test_single_url(), test_single_with_timestamps() (+1 more)

### Community 18 - "Streaming Demo Server"
Cohesion: 0.31
Nodes (8): api_chunk(), api_finish(), api_start(), _gc_sessions(), _get_session(), main(), parse_args(), Session

### Community 19 - "vLLM Streaming Examples"
Cohesion: 0.48
Nodes (6): _download_audio_bytes(), main(), Simple resample to 16k if needed (uses linear interpolation; good enough for a t, _read_wav_from_bytes(), _resample_to_16k(), run_streaming_case()

### Community 20 - "Rotary Position Embedding"
Cohesion: 0.5
Nodes (2): Qwen3ASRThinkerTextRotaryEmbedding, Apply interleaved MRoPE to 3D rotary embeddings.         Reorganizes frequency

### Community 21 - "CLI Entry Point"
Cohesion: 1.0
Nodes (0): 

### Community 22 - "vLLM Serve CLI"
Cohesion: 1.0
Nodes (0): 

### Community 23 - "Aligner Rationale"
Cohesion: 1.0
Nodes (1): Load Qwen3-ForcedAligner model and initialize processors.          This method

### Community 24 - "Aligner Rationale"
Cohesion: 1.0
Nodes (1): Run forced alignment for batch or single sample.          Args:             a

## Knowledge Gaps
- **52 isolated node(s):** `Simple resample to 16k if needed (uses linear interpolation; good enough for a t`, `Download audio bytes from a URL.      Args:         url (str): Audio URL.`, `Decode audio bytes into waveform and sampling rate.      Args:         audio_`, `Convert audio bytes into a base64 data URL string.      Args:         audio_b`, `Print a compact summary for debugging.      Args:         title (str): Case n` (+47 more)
  These have ¡Ü1 connection - possible missing edges or undocumented components.
- **Thin community `CLI Entry Point`** (2 nodes): `main()`, `__main__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `vLLM Serve CLI`** (2 nodes): `serve.py`, `main()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Aligner Rationale`** (1 nodes): `Load Qwen3-ForcedAligner model and initialize processors.          This method`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Aligner Rationale`** (1 nodes): `Run forced alignment for batch or single sample.          Args:             a`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Qwen3ASRConfig` connect `Config and Attention` to `Inference Engine Internals`, `Audio Processor`, `Audio Encoder Architecture`, `Model Configuration`, `Rotary Embeddings and MLP`, `Audio Encoder Module`, `Pretrained Model Base`, `Thinker Conditional Generation`, `Rotary Position Embedding`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `Qwen3ASRAudioEncoderConfig` connect `Pretrained Model Base` to `Inference Engine Internals`, `Audio Processor`, `Audio Encoder Architecture`, `Model Configuration`, `Config and Attention`, `Rotary Embeddings and MLP`, `Audio Encoder Module`, `Thinker Conditional Generation`, `Rotary Position Embedding`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `Qwen3ASRThinkerConfig` connect `Model Configuration` to `Inference Engine Internals`, `Audio Processor`, `Audio Encoder Architecture`, `Config and Attention`, `Rotary Embeddings and MLP`, `Audio Encoder Module`, `Pretrained Model Base`, `Thinker Conditional Generation`, `Rotary Position Embedding`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 60 inferred relationships involving `Qwen3ASRAudioEncoderConfig` (e.g. with `Qwen3ASRTextRMSNorm` and `Qwen3ASRTextAttention`) actually correct?**
  _`Qwen3ASRAudioEncoderConfig` has 60 INFERRED edges - model-reasoned connections that need verification._
- **Are the 60 inferred relationships involving `Qwen3ASRThinkerConfig` (e.g. with `Qwen3ASRTextRMSNorm` and `Qwen3ASRTextAttention`) actually correct?**
  _`Qwen3ASRThinkerConfig` has 60 INFERRED edges - model-reasoned connections that need verification._
- **Are the 60 inferred relationships involving `Qwen3ASRConfig` (e.g. with `Qwen3ASRTextRMSNorm` and `Qwen3ASRTextAttention`) actually correct?**
  _`Qwen3ASRConfig` has 60 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `Qwen3ASRProcessor` (e.g. with `SinusoidsPositionEmbedding` and `Qwen3ASRAudioAttention`) actually correct?**
  _`Qwen3ASRProcessor` has 19 INFERRED edges - model-reasoned connections that need verification._