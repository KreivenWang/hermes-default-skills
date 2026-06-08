---
name: task-routing-gateway
description: "智能任务路由网关：评估任务难度和语言精细度，LOW → 本地 Qwen3.5-9B, HIGH → DeepSeek v4 Flash API"
version: 1.0.0
author: Hermes Agent
tags: [routing, classification, local-model, api-model, task-decomposition]
---

# 智能任务路由网关

该技能实现了一个前置判断机制：在每次执行用户任务前，先评估任务难度，然后路由到合适的模型执行。

## 模型资源

| 等级 | 目标模型 | 访问方式 |
|------|---------|---------|
| 🔴 HIGH | `deepseek-v4-flash` (API) | 当前 session 默认模型 (DeepSeek API) |
| 🟢 LOW | `Qwen3.5-9B-Q4_K_M` (本地) | `http://localhost:8080/v1/chat/completions` (OpenAI 兼容 API) |

## 分类标准

### 🟢 LOW — 简单任务
直接通过 `curl` 调用本地模型，**不经过主 agent**。

满足以下任意一条即可判定为 LOW：
- **纯数据抓取**：抓取网页内容、RSS、API 数据
- **数据清洗/格式化**：HTML/JSON/CSV 转换、文本去重、批量重命名
- **简单翻译**：单词/短句翻译、中英对照
- **简单文本处理**：纯文本格式调整、大小写转换、排序
- **日常查询**：天气、时间、日期计算、基础数学
- **无深度润色**：简单的语法修正、标点统一（不需要改变文章结构和风格）
- **单步骤操作**：执行一个确定的命令（ls, cat, git status 等）

### 🔴 HIGH — 复杂任务
由当前 session 默认的 API 模型（deepseek-v4-flash）处理。

满足以下任意一条即可判定为 HIGH：
- **学术出题**：设计雅思真题干扰项、考试题目、编程竞赛题等需要严谨逻辑的任务
- **复杂逻辑推理**：数学证明、算法设计、形式化验证、因果推理
- **深度多源观点提炼**：需要从多个来源综合对比、分析趋势、提炼核心观点
- **地道长文创作**：文学创作、深度技术文章、演讲稿、商业文案润色（需要改变风格/语气/结构）
- **多步骤编排**：需要调用多个工具、跨文件操作、有条件分支的复杂流程
- **代码生成/审查**：需要编写复杂算法、重构、调试、安全审查
- **需要外部知识**：涉及专业领域知识（法律、医学、金融等）
- **用户明确指定使用 API 模型**

## 路由流程

```
用户输入
    │
    ▼
┌─────────────────┐
│  分类判断        │  ← 当前 agent 评估任务难度
│  LOW or HIGH?    │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
  🟢 LOW    🔴 HIGH
    │         │
    ▼         ▼
curl 本地    当前 session
Qwen3.5-9B  DeepSeek v4 Flash
(无需主agent  (主agent正常
 处理)        处理)
```

## 分类输出格式

在对话中执行分类时，先输出一行分类结果，然后根据结果执行：

```
[🧠 路由网关] 任务判定: 🟢 LOW (原因: 纯数据抓取)
```

或

```
[🧠 路由网关] 任务判定: 🔴 HIGH (原因: 复杂逻辑推理)
```

## 本地模型调用方法

### 标准 API 调用 (OpenAI 兼容)

```bash
curl -s http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.5-9B-Q4_K_M.gguf",
    "messages": [{"role": "user", "content": "用户问题"}],
    "temperature": 0.7,
    "max_tokens": 4096
  }' | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])"
```

### 流式（Streaming）调用

```bash
curl -s -N http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3.5-9B-Q4_K_M.gguf",
    "messages": [{"role": "user", "content": "你好"}],
    "temperature": 0.7,
    "max_tokens": 4096,
    "stream": true
  }' | while read -r line; do
    [[ "$line" =~ ^data: ]] && echo -n "$(echo "$line" | sed 's/^data: //' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('choices',[{}])[0].get('delta',{}).get('content','')if'data' not in json.load(sys.stdin)else'',end='')" 2>/dev/null)"
  done
```

### 在 execute_code 中使用

```python
from hermes_tools import terminal
r = terminal("""curl -s http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"Qwen3.5-9B-Q4_K_M.gguf","messages":[{"role":"user","content":"简单任务"}],"temperature":0.7,"max_tokens":4096}'""")
import json
result = json.loads(r["output"])
print(result["choices"][0]["message"]["content"])
```

### 在 execute_code 中使用（Python 原生，无 shell）

```python
import json, urllib.request, socket
socket.setdefaulttimeout(60)
payload = json.dumps({
    "model": "Qwen3.5-9B-Q4_K_M.gguf",
    "messages": [{"role": "user", "content": "简单任务"}],
    "temperature": 0.7,
    "max_tokens": 4096
}).encode()
req = urllib.request.Request(
    "http://localhost:8080/v1/chat/completions",
    data=payload, headers={"Content-Type": "application/json"}, method="POST"
)
with urllib.request.urlopen(req, timeout=60) as resp:
    d = json.loads(resp.read())
result = d["choices"][0]["message"].get("content", "")
reasoning = d["choices"][0]["message"].get("reasoning_content", None)
# result 是模型回复，reasoning 是思维链（若有）
```

### 快捷脚本

```bash
python3 ~/.hermes/skills/hermes/task-routing-gateway/scripts/local_qwen.py "你的问题"
```

## 注意事项

1. **本地模型能力边界**：Qwen3.5-9B-Q4_K_M 是量化模型，不支持复杂推理、长文创作、代码审查等。强行使用可能导致结果不可靠。
2. **context length**：本地模型配置了 131072 token 的上下文，足以处理中等长度文本。
3. **并发限制**：`-np 1` 表示一次只能处理一个请求。如遇并发，排队等待。
4. **纯数据任务**：对于纯数据抓取/格式化，甚至不需要调用 LLM，直接用 shell 命令或 Python 处理即可。
5. **API 不可用时**：如果 DeepSeek API 不可用，所有路由都降级到本地模型。
6. **用户覆盖**：用户可明确指定 "用本地模型" 或 "用 API 模型" 来覆盖自动分类。
