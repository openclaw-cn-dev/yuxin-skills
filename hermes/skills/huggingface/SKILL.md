---
name: huggingface
description: "Hugging Face ecosystem — model discovery, local inference, training, evaluation, datasets, Gradio UIs, paper publishing, experiment tracking, and tooling. Load the relevant subsection or see references/ for full content."
version: 1.0.0
license: MIT
tags: [huggingface, ml, training, inference, datasets, gradio, evaluation]
related_skills: [huggingface-hub, llama-cpp, vllm, mlops]
---

# Hugging Face Ecosystem

A unified entry point for the Hugging Face ecosystem. Each subsection below is a thin routing layer — the full detailed content for each topic lives in `references/<skill-name>.md`.

## Quick Routing

| Task | Subsection / Reference |
|------|-----------------------|
| Find best model for a task | → `references/huggingface-best.md` |
| Run community evals (inspect-ai, lighteval) | → `references/huggingface-community-evals.md` |
| Explore datasets via HF API | → `references/huggingface-datasets.md` |
| Build Gradio UIs and demos | → `references/huggingface-gradio.md` |
| Train LLMs on HF Jobs (SFT/DPO/GRPO) | → `references/huggingface-llm-trainer.md` |
| Run GGUF models locally (llama.cpp) | → `references/huggingface-local-models.md` |
| Publish papers to HF Hub | → `references/huggingface-paper-publisher.md` |
| Browse HF Paper Pages | → `references/huggingface-papers.md` |
| Build HF API CLI tools | → `references/huggingface-tool-builder.md` |
| Log ML experiments (Trackio) | → `references/huggingface-trackio.md` |
| Train vision models on HF Jobs | → `references/huggingface-vision-trainer.md` |

## Common Patterns

### Hub API Basics
```bash
# Search models
hf ls --type model --sort downloads --direction -1 | head -20

# Download a model
hf download meta-llama/Llama-3-8B-Instruct

# Upload a file
hf upload your-username/your-repo path/to/file

# Model info
hf info meta-llama/Llama-3-8B-Instruct
```

### Authentication
```bash
# Login (get token from https://huggingface.co/settings/tokens)
hf login
```

### Quick Device Check
```bash
# Check GPU
nvidia-smi

# Check Metal (Mac)
python3 -c "import torch; print('Metal:', torch.backends.mps.is_available())"

# Check CPU
python3 -c "import torch; print('CPU:', torch.cuda.is_available() == False)"
```

## Subsections

### Model Discovery (`references/huggingface-best.md`)
Finds the best models for a task by querying official HF benchmark leaderboards. Enriches results with model size data and filters for device fit.

**Trigger:** "find the best model for X", "which model should I use for coding/math/chat/RAG/OCR", "model recommendation"

### Community Evals (`references/huggingface-community-evals.md`)
Run evaluations against HF Hub models on local hardware using `inspect-ai` or `lighteval`. Covers vLLM/HuggingFace/accelerate backends, smoke tests, and task selection.

**Trigger:** "run evals on HF model", "benchmark my model", "evaluate model performance"

### Dataset Explorer (`references/huggingface-datasets.md`)
Execute read-only Dataset Viewer API calls: validate datasets, resolve configs/splits, preview rows, paginate, search, filter, retrieve parquet links.

**Trigger:** "explore a dataset", "get rows from dataset X", "search dataset for text"

### Gradio UI (`references/huggingface-gradio.md`)
Build interactive web UIs and ML demos with Gradio. Covers Interface class, Blocks, layout, event listeners, authentication, and deployment to HF Spaces.

**Trigger:** "build a Gradio demo", "create a web UI for my model", "deploy to HF Spaces"

### LLM Training on HF Jobs (`references/huggingface-llm-trainer.md`)
Train language models using TRL (SFT, DPO, GRPO, Reward Modeling) on fully managed HF cloud GPUs. No local GPU setup. Results auto-saved to HF Hub.

**Trigger:** "fine-tune an LLM", "train with DPO", "RLHF training job", "SFT on HF"

### Local GGUF Inference (`references/huggingface-local-models.md`)
Search HF Hub for llama.cpp-compatible GGUF repos, select quantisation level, and launch with `llama-cli` or `llama-server`. Covers Metal/CPU/colab local inference.

**Trigger:** "run model locally", "GGUF inference", "llama.cpp setup", "run model on Mac"

### Paper Publishing (`references/huggingface-paper-publisher.md`)
Publish and manage research papers on the HF Hub. Integrates with arXiv, links papers to models/datasets, manages authorship.

**Trigger:** "publish paper to HF", "link paper to model", "submit to hf.co/papers"

### Paper Pages (`references/huggingface-papers.md`)
Browse, search, and track papers on HF Paper Pages (hf.co/papers). Submit papers, manage author claims, track daily papers feed.

**Trigger:** "find papers on HF", "what papers are trending", "submit paper to HF"

### API Tool Builder (`references/huggingface-tool-builder.md`)
Create reusable CLI scripts using the HF API. Covers `hf` CLI, model/dataset card access, API endpoints, chaining and piping.

**Trigger:** "script HF API call", "build HF CLI tool", "automate model upload"

### Experiment Tracking (`references/huggingface-trackio.md`)
Log ML training metrics with Trackio. Three interfaces: Python API for metrics, Python API for alerts, CLI for spaces sync. Synced to HF Spaces for dashboards.

**Trigger:** "track training metrics", "log experiment", "monitor training live"

### Vision Model Training (`references/huggingface-vision-trainer.md`)
Train object detection (D-FINE, RT-DETR v2, DETR, YOLOS), image classification (ViT, ResNet, MobileViT), and SAM/SAM2 segmentation on managed cloud GPUs.

**Trigger:** "train object detection model", "fine-tune vision model", "train on HF Jobs vision"
