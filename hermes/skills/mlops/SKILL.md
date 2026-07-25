---
name: mlops
description: ML operations — model serving, training, evaluation, inference, and research tooling. Load this umbrella when you need to pick a tool for serving LLMs, fine-tuning, evaluating models, building vector search, or running research frameworks like DSPy.
version: 1.0.0
metadata:
  hermes:
    tags: [mlops, llm, inference, training, evaluation, huggingface, vector-database]
---

# MLOps — Model Operations & Research Tooling

Class-level umbrella for ML/LLM operations tooling. Organized by **phase of the ML lifecycle**.

## Sub-umbrellas (load the right one)

- `inference/` — Model serving, quantization (GGUF/GPTQ), structured output, inference optimization.
- `training/` — Fine-tuning, RLHF/DPO/GRPO training, distributed training frameworks.
- `evaluation/` — Benchmarks, experiment tracking, data curation, tokenizers.
- `models/` — Specific model architectures and tools.
- `research/` — ML research frameworks for declarative programming.
- `vector-databases/` — Vector databases, embeddings, retrieval.

## Direct children

- `huggingface-hub/` — `hf` CLI for search/download/upload of models and datasets (used across all phases).

## How to choose

- **Run a model locally** → `inference/llama-cpp/` or `inference/vllm/`
- **Fine-tune** → `training/unsloth/`, `training/axolotl/`, or `training/trl-fine-tuning/`
- **Evaluate** → `evaluation/lm-evaluation-harness/` or `evaluation/weights-and-biases/`
- **Build a RAG stack** → `vector-databases/` + `inference/` for the embedding model
- **Use HuggingFace datasets/models** → `huggingface-hub/` (cross-cutting)
- **Generate music / images with ML** → `models/audiocraft/` or `models/segment-anything/`
- **Use DSPy for prompt optimization** → `research/dspy/`
- **Remove model refusals** → `inference/obliteratus/`
- **Structured JSON/regex output** → `inference/outlines/`
