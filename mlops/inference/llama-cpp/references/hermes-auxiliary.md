# Hermes Agent Auxiliary Tasks via llama-server

When Hermes uses a local llama-server (e.g. `Qwen3.5-9B-Q4_K_M.gguf`) for its auxiliary tasks — vision, compression, approval, curator, etc. — the `config.yaml` must point each task's `base_url` at the server.

## Config Structure

Hermes auxiliary tasks live under `auxiliary:` in `~/.hermes/config.yaml`:

```yaml
auxiliary:
  vision:
    provider: custom
    model: Qwen3.5-9B-Q4_K_M.gguf
    base_url: http://127.0.0.1:8080/v1
    api_key: ''
    timeout: 120
  compression:
    provider: custom
    model: Qwen3.5-9B-Q4_K_M.gguf
    base_url: http://127.0.0.1:8080/v1
    api_key: ''
    timeout: 120
  approval:
    provider: custom
    model: Qwen3.5-9B-Q4_K_M.gguf
    base_url: http://127.0.0.1:8080/v1
    api_key: ''
    timeout: 30
```

### Tasks that commonly use the local model

| Task | Typical timeout | Purpose |
|------|----------------|---------|
| `vision` | 120s | Image analysis |
| `web_extract` | 360s | Web page content extraction |
| `compression` | 120s | Context window compression |
| `approval` | 30s | Dangerous command approval helper |
| `curator` | 600s | Skill lifecycle maintenance |
| `title_generation` | 30s | Session title generation |
| `mcp` | 30s | MCP server interaction |
| `skills_hub` | 30s | Skill search/browse |
| `flush_memories` | 30s | Memory flushing |
| `session_search` | 30s | Cross-session search |
| `triage_specifier` | 120s | Task routing classification |
| `kanban_decomposer` | 180s | Task decomposition |
| `profile_describer` | 60s | Profile description |

## Common Pitfall: Empty base_url

If a task uses `provider: custom` but has `base_url: ''` (empty string), the auxiliary client will fail silently — it tries to connect to nowhere.

**Symptoms:**
- The main model (e.g. DeepSeek via API) works fine
- Auxiliary features like context compression silently fail
- Cron jobs log warnings like `Vision auto-detect: using main provider custom (Qwen3.5-9B)` but never actually use the model
- No error is thrown — the system falls back to the main provider or skips the auxiliary step

**Fix:** Point each task's `base_url` to the running llama-server:

```bash
cd ~/.hermes && ~/.hermes/hermes-agent/venv/bin/python3 << 'PYEOF'
import yaml
cfg = yaml.safe_load(open('config.yaml'))
local = 'http://127.0.0.1:8080/v1'
for name, task in cfg.get('auxiliary', {}).items():
    if isinstance(task, dict) and task.get('provider') == 'custom' and not task.get('base_url'):
        task['base_url'] = local
yaml.dump(cfg, open('config.yaml','w'), default_flow_style=False, indent=2, sort_keys=False)
print(f'Fixed {sum(1 for _ in [])} tasks')  # count manually
PYEOF
hermes gateway restart
```

## Reasoning Models (Qwen3.5 Behavior)

Qwen3.5 models include a `reasoning_content` field in chat completions. The model first emits its thinking process in `reasoning_content`, then the final answer in `content`.

**Important:** With very low `max_tokens` (e.g. 20), only `reasoning_content` is generated — `content` will be empty. Ensure `max_tokens` is at least 200 for auxiliary tasks to leave room for the thinking phase.

Example response structure:
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "最终答案",
      "reasoning_content": "Thinking Process:\n1. 分析问题..."
    }
  }],
  "usage": { "completion_tokens": 113 }
}
```

## Verification

Test the server and Hermes config with:

```bash
# 1. Server health
curl -s http://127.0.0.1:8080/v1/models | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data'][0]['id'])"

# 2. Inference test (enough tokens for reasoning + content)
curl -s http://127.0.0.1:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"Qwen3.5-9B-Q4_K_M.gguf","messages":[{"role":"user","content":"测试：只回复\"好\"一个字"}],"max_tokens":200}' \
  --max-time 30 | python3 -c "import sys,json; d=json.load(sys.stdin); print('Content:', d['choices'][0]['message']['content'])"

# 3. Hermes auxiliary config check
grep -A3 "base_url:" ~/.hermes/config.yaml | grep "8080" | wc -l
# Should show 11+ tasks pointing at localhost:8080
```
