#!/usr/bin/env python3
"""简易接口：调用本地 Qwen3.5-9B 模型"""
import sys, json, urllib.request

def ask_local(prompt: str, temperature: float = 0.7, max_tokens: int = 4096) -> str:
    """调用本地 llama-server API 并返回文本回复"""
    payload = json.dumps({
        "model": "Qwen3.5-9B-Q4_K_M.gguf",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }).encode()

    req = urllib.request.Request(
        "http://localhost:8080/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 local_qwen.py <提示词>", file=sys.stderr)
        sys.exit(1)
    prompt = " ".join(sys.argv[1:])
    try:
        result = ask_local(prompt)
        print(result)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
