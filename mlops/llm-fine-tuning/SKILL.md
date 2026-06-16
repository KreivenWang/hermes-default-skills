---
name: llm-fine-tuning
description: "Complete LLM fine-tuning workflow: framework selection (Axolotl, TRL, Unsloth), config management, training execution, and evaluation. Includes LoRA/QLoRA, DPO/ORPO/GRPO, and multimodal support."
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [fine-tuning, lora, qlora, dpo, grpo, rlhf, axolotl, trl, unsloth, huggingface]
category: mlops
---

# LLM Fine-Tuning Umbrella Skill

This umbrella skill covers the complete LLM fine-tuning workflow across multiple frameworks. Use the subsections below to guide specific framework choices and configurations.

## Framework Selection Guide

| Framework | Best For | Speed | Memory | Learning Curve |
|-----------|----------|-------|--------|----------------|
| **Axolotl** | Production deployments, YAML configs, DeepSpeed integration | Medium | Medium | Medium |
| **TRL (Transformers Reinforcement Learning)** | RLHF research, DPO/ORPO/GRPO algorithms | Medium | Medium | Medium |
| **Unsloth** | Fast prototyping, 2-5x faster training, 50-80% less memory | Fast | Low | Easy |

## Subsection References

### Axolotl Fine-Tuning
See `references/axolotl-guide.md` for detailed Axolotl configuration, YAML patterns, and deployment workflows.

### TRL Fine-Tuning (DPO/ORPO/GRPO)
See `references/trl-guide.md` for reinforcement learning algorithms, reward modeling, and preference alignment.

### Unsloth Fast Training
See `references/unsloth-guide.md` for memory-efficient training, LoRA optimization, and rapid prototyping patterns.

## Common Patterns

### Pattern 1: LoRA Configuration
```yaml
ranks:
  - lora_r: 16
    lora_alpha: 32
    target_modules: ["q_proj", "v_proj"]
```

### Pattern 2: QLoRA with 4-bit Quantization
```yaml
quantization:
  type: "nf4"
  dtype: "fp16"
  ckpt_path: "path/to/quantized"
```

### Pattern 3: DPO Training (Preference Alignment)
```yaml
dpo_beta: 0.1
reference_model: "path/to/ref/model"
```

## Workflow

1. **Select Framework** — Based on use case (production vs research vs rapid prototyping)
2. **Prepare Data** — Clean, format, and validate training datasets
3. **Configure Training** — Set hyperparameters, LoRA ranks, and batch sizes
4. **Execute Training** — Monitor losses and validate checkpoints
5. **Evaluate Results** — Run benchmarks and compare against base model

## Related Skills

- `evaluating-llms-harness` — Benchmark fine-tuned models
- `weights-and-biases` — Experiment tracking
- `huggingface-hub` — Model registry and sharing

---

## Section: Axolotl Fine-Tuning

Comprehensive guidance for Axolotl-based fine-tuning workflows.

### When to Use Axolotl

- Production deployments with YAML configuration
- Multi-GPU training with DeepSpeed integration
- Complex setups requiring FSDP, context parallelism
- Saving compressed models for vLLM inference

### Common Patterns

**Pattern 1: Validate Data Transfer Speeds**
```bash
./build/all_reduce_perf -b 8 -e 128M -f 2 -g 3
```

**Pattern 2: Configure FSDP**
```yaml
fsdp_version: 2
fsdp_config:
  offload_params: true
  state_dict_type: FULL_STATE_DICT
  auto_wrap_policy: TRANSFORMER_BASED_WRAP
  transformer_layer_cls_to_wrap: LlamaDecoderLayer
  reshard_after_forward: true
```

**Pattern 3: Context Parallelism Settings**
- context_parallel_size must be a divisor of total GPUs
- Example: 8 GPUs with context_parallel_size=4 → only 2 batches per step

**Pattern 4: Compressed Model Saving**
```yaml
save_compressed: true
```
Benefits:
- Reduces disk space by ~40%
- Maintains vLLM compatibility
- Enables llmcompressor optimization

### References

- `references/axolotl-guide.md` — Complete Axolotl documentation
- `references/api.md` — API reference
- `references/dataset-formats.md` — Dataset format specifications

---

## Section: TRL Fine-Tuning (DPO/ORPO/GRPO)

Reinforcement learning fine-tuning for alignment and preference optimization.

### When to Use TRL

- RLHF research and experiments
- DPO (Direct Preference Optimization) for preference alignment
- ORPO (Odds Ratio Preference Optimization)
- GRPO (Group Relative Policy Optimization)
- PPO with reward models

### Algorithms

| Algorithm | Purpose | Complexity |
|-----------|---------|------------|
| **SFT (Supervised Fine-Tuning)** | Instruction tuning | Low |
| **DPO** | Preference alignment | Medium |
| **ORPO** | Preference alignment with reduced data | Medium |
| **GRPO** | Group-based reward optimization | High |
| **PPO** | Full RLHF with reward models | Very High |

### Common Patterns

**Pattern 1: DPO Configuration**
```yaml
dpo_beta: 0.1
reference_model: "path/to/ref/model"
loss_type: "sigmoid"
```

**Pattern 2: ORPO Configuration**
```yaml
orpo_loss_coef: 1.0
orpo_reference_free: true
```

**Pattern 3: GRPO Configuration**
```yaml
n_per_prompt: 4
gamma: 0.95
```

### References

- `references/trl-guide.md` — Complete TRL documentation
- `references/dpo-guide.md` — DPO-specific patterns
- `references/orpo-guide.md` — ORPO-specific patterns

---

## Section: Unsloth Fast Training

Memory-efficient, high-speed fine-tuning for rapid prototyping.

### When to Use Unsloth

- 2-5x faster training than baseline
- 50-80% less memory usage
- LoRA/QLoRA optimization
- Llama, Mistral, Gemma, Qwen support

### Key Features

- **Memory Efficiency**: 4-bit quantization, kernel optimizations
- **Speed**: Up to 5x faster training
- **Easy Integration**: Simple API, minimal config changes
- **Model Support**: Llama, Mistral, Gemma, Qwen

### References

- `references/unsloth-guide.md` — Complete Unsloth documentation
- `references/llms.md` — Supported model list
- `references/llms-txt.md` — LLaMA-specific patterns

---

## Section: Data Preparation

### Dataset Format

```json
{
  "prompt": "User input here",
  "chosen": "Preferred response",
  "rejected": "Unpreferred response"
}
```

### Cleaning Pipeline

1. Remove duplicates
2. Filter low-quality samples
3. Validate JSON structure
4. Check for PII/secrets
5. Split into train/val/test

---

## Section: Evaluation

After fine-tuning, evaluate using:

- `evaluating-llms-harness` — Standard benchmarks (MMLU, GSM8K, etc.)
- Custom evaluation scripts
- Human feedback collection

---

## Section: Experiment Tracking

Use `weights-and-biases` for:
- Logging hyperparameters
- Tracking losses
- Visualizing runs
- Model registry

---

## Section: Model Sharing

Use `huggingface-hub` to:
- Upload fine-tuned models
- Share configurations
- Document training details
- Generate model cards