---
name: llm-inference
description: "Complete LLM inference serving guide: llama.cpp (CPU/edge) + vLLM (GPU/production), model discovery, quantization, deployment, and optimization."
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [llm, inference, llama.cpp, vllm, gguf, quantization, deployment, serving]
category: mlops
---

# LLM Inference Umbrella Skill

This umbrella skill covers LLM inference serving across different platforms and use cases. Use the subsections below to guide specific deployment choices.

## Platform Selection Guide

| Platform | Best For | Hardware | Throughput | Use Case |
|----------|----------|----------|------------|----------|
| **llama.cpp** | CPU/edge inference, portability | CPU, Apple Silicon, CUDA, ROCm | Low-Medium | Local, portable, single-user |
| **vLLM** | Production APIs, high throughput | NVIDIA GPU (primary) | High | Multi-user, production APIs |

## Subsection References

### llama.cpp (CPU/Edge Inference)
See `references/llama-cpp-guide.md` for detailed llama.cpp configuration, GGUF patterns, and edge deployment.

### vLLM (GPU/Production Serving)
See `references/vllm-guide.md` for production deployment, OpenAI API integration, and high-throughput optimization.

## Common Workflows

### Workflow 1: Local Inference (llama.cpp)

```bash
# Quick start from Hub
llama-cli -hf bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0

# Or run server
llama-server -hf bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0
```

### Workflow 2: Production API (vLLM)

```bash
# Basic deployment
vllm serve meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --port 8000

# With quantization
vllm serve TheBloke/Llama-2-70B-AWQ \
  --quantization awq \
  --tensor-parallel-size 4 \
  --gpu-memory-utilization 0.95
```

---

## Section: llama.cpp (CPU/Edge Inference)

Comprehensive guidance for llama.cpp local inference, GGUF handling, and edge deployment.

### When to Use llama.cpp

- Run local models on CPU, Apple Silicon, CUDA, ROCm, or Intel GPUs
- Find the right GGUF for a specific Hugging Face repo
- Build llama-server or llama-cli commands from the Hub
- Search the Hub for models that already support llama.cpp
- Edge deployment, portable inference
- Single-user, offline scenarios

### Key Features

- **GGUF Format**: Universal quantized model format
- **Platform Support**: CPU, Apple Silicon (Metal), CUDA, ROCm, Intel GPUs
- **Portability**: Single binary, no special drivers
- **Edge Deployment**: Runs on low-resource devices
- **Open Source**: MIT license, actively maintained

### Model Discovery

1. Search for candidate repos:
   - `https://huggingface.co/models?apps=llama.cpp&sort=trending`
   - Add `search=<term>` for specific model family
   - Add `num_parameters=min:0,max:24B` for size constraints

2. Open the repo with llama.cpp local-app view:
   - `https://huggingface.co/<repo>?local-app=llama.cpp`

3. Extract the exact `llama-server` or `llama-cli` command

### Quantization Guide

- **Q4_K_M**: General purpose, good quality/size balance
- **Q5_K_M**: Code/technical work, better quality
- **Q6_K**: Near-lossless, higher memory
- **Q3_K_M**: Tight RAM budgets
- **IQ variants**: Integer quantization, very efficient

### Quick Start

```bash
# Install
brew install llama.cpp

# Run from Hub
llama-cli -hf bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0

# Run server
llama-server -hf bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0

# Python bindings
pip install llama-cpp-python
```

### References

- `references/llama-cpp-guide.md` — Complete llama.cpp documentation
- `references/hub-discovery.md` — Hub search patterns and GGUF extraction
- `references/quantization.md` — Quant quality tradeoffs
- `references/server.md` — Server launch and OpenAI API endpoints
- `references/optimization.md` — CPU threading, GPU offload heuristics
- `references/troubleshooting.md` — Common issues and solutions

---

## Section: vLLM (GPU/Production Serving)

Comprehensive guidance for vLLM high-throughput production deployment.

### When to Use vLLM

- Deploying production LLM APIs (100+ req/sec)
- Serving OpenAI-compatible endpoints
- Limited GPU memory but need large models
- Multi-user applications (chatbots, assistants)
- Need low latency with high throughput

### Key Features

- **PagedAttention**: Block-based KV cache, 24x throughput improvement
- **Continuous Batching**: Mix prefill/decode requests
- **Tensor Parallelism**: Scale across multiple GPUs
- **Quantization**: GPTQ/AWQ/FP8 support
- **OpenAI API**: Drop-in compatibility

### Production Deployment

```bash
# Basic deployment
vllm serve meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --max-model-len 8192 \
  --port 8000

# With tensor parallelism
vllm serve meta-llama/Llama-2-70B-hf \
  --tensor-parallel-size 4 \
  --gpu-memory-utilization 0.9 \
  --quantization awq \
  --port 8000

# Production with monitoring
vllm serve meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --enable-prefix-caching \
  --enable-metrics \
  --metrics-port 9090 \
  --port 8000 \
  --host 0.0.0.0
```

### Quantization Methods

- **AWQ**: Best for 70B models, minimal accuracy loss
- **GPTQ**: Wide model support, good compression
- **FP8**: Fastest on H100 GPUs

### Performance Monitoring

Key metrics:
- `vllm:time_to_first_token_seconds` — Latency
- `vllm:num_requests_running` — Active requests
- `vllm:gpu_cache_usage_perc` — KV cache utilization

### References

- `references/vllm-guide.md` — Complete vLLM documentation
- `references/server-deployment.md` — Docker, Kubernetes, load balancing
- `references/optimization.md` — PagedAttention tuning, benchmarks
- `references/quantization.md` — AWQ/GPTQ/FP8 setup
- `references/troubleshooting.md` — Error messages and diagnostics

---

## Section: Model Discovery

### Hugging Face Hub Search

```text
https://huggingface.co/models?apps=llama.cpp&sort=trending
https://huggingface.co/models?search=<term>&apps=llama.cpp&sort=trending
https://huggingface.co/models?search=<term>&apps=llama.cpp&num_parameters=min:0,max:24B&sort=trending
https://huggingface.co/<repo>?local-app=llama.cpp
https://huggingface.co/api/models/<repo>/tree/main?recursive=true
```

### Extract GGUF Files

Use the tree API:
- `https://huggingface.co/api/models/<repo>/tree/main?recursive=true`

Filter for `.gguf` files and extract:
- filename
- file size
- quant label
- whether main model or projector

---

## Section: Quantization Guide

### Quality vs Size Tradeoffs

| Quant | Size Reduction | Quality | Use Case |
|-------|---------------|---------|----------|
| Q8_0 | ~2x | Lossless | Reference, testing |
| Q5_K_M | ~3x | High | Production, general use |
| Q4_K_M | ~4x | Good | Default recommendation |
| Q3_K_M | ~5x | Medium | Tight memory budgets |
| IQ2_XXS | ~6x | Low | Edge devices |

### Selection Heuristics

- **General chat**: Q4_K_M
- **Code/technical**: Q5_K_M or Q6_K
- **Tight RAM**: Q3_K_M, IQ variants
- **Multimodal**: Check for `mmproj-*.gguf` separately

---

## Section: Hardware Requirements

### llama.cpp

- **Small models (7B-13B)**: Modern CPU or Apple M1+
- **Medium models (30B-40B)**: 1x A100 (40GB) or 2x A10 (24GB)
- **Large models (70B+)**: 2-4x A100 (40GB) with TP

### vLLM

- **Small models (7B-13B)**: 1x A10 (24GB) or A100 (40GB)
- **Medium models (30B-40B)**: 2x A100 (40GB) with TP
- **Large models (70B+)**: 4x A100 (40GB) or 2x A100 (80GB)

---

## Section: Troubleshooting

### Common Issues

**Out of memory:**
```bash
vllm serve MODEL --gpu-memory-utilization 0.7 --max-model-len 4096
```

**Slow first token:**
```bash
vllm serve MODEL --enable-prefix-caching --enable-chunked-prefill
```

**Model not found:**
```bash
vllm serve MODEL --trust-remote-code
```

**Low throughput:**
```bash
vllm serve MODEL --max-num-seqs 512
```

---

## Section: Related Skills

- `llm-fine-tuning` — Fine-tune models before inference
- `evaluating-llms-harness` — Benchmark fine-tuned models
- `weights-and-biases` — Experiment tracking for inference runs
- `huggingface-hub` — Model registry and sharing