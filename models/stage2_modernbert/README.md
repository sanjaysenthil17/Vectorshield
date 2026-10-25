# Stage 2 ModernBERT Neural Classifier Checkpoint

This directory contains the fine-tuned checkpoint configuration, tokenizer files, and vocabulary for **Vector-Shield Stage 2 Deep Sequence Classification**.

## Model Architecture & Training Summary
- **Base Model**: `answerdotai/ModernBERT-base` (149M parameters, 8192 context window)
- **Training Node**: NVIDIA A100 80GB PCIe GPU
- **Dataset**: Scaled enterprise corpus (`data/vector_shield_scaled_corpus.jsonl`) with real prompt injection payloads (Garak, HuggingFace deepset)
- **Batch Size**: 16
- **Epochs**: 3
- **Mixed Precision**: FP16 enabled (`torch.cuda.amp`)
- **Learning Rate**: 2e-5 with AdamW and linear warmup

## Validation Telemetry
- **Final Training Loss**: `0.0625`
- **Validation Accuracy**: `100.00%`
- **Precision (Injection)**: `100.00%`
- **Recall (Injection)**: `100.00%`
- **F1 Score**: `100.00%`

## Checkpoint Files
- `config.json`: Model configuration and sequence classification head mapping
- `model.safetensors`: Fine-tuned PyTorch tensor weights (~598 MB, retained on the GPU node storage)
- `tokenizer.json`: Fast tokenizer configuration
- `tokenizer_config.json`: ModernBERT tokenizer configuration
- `special_tokens_map.json`: Special tokens mapping
