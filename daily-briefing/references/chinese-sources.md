# 中文 AI 新闻来源访问指南

## 已验证可用的中文 AI 来源

### 雷锋网 AI — leiphone.com/category/ai
**最佳中文 AI 来源。** 标题以 `title` 属性嵌入 `<a>` 标签，正则一次性提取。

```python
re.findall(r'<a[^>]*href="(https?://[^"]+\.html)"[^>]*title="([^"]+)"', html)
```

提取的标题示例：SoulAgent 智源大会、CVPR 2026 总结、华为天才少年创业、GuidedVLA 机器人等。

## 不可用的中文 AI 来源

| 来源 | URL | 原因 |
|------|-----|------|
| 机器之心 | jiqizhixin.com | HTML 结构复杂，标题提取不可靠 |
| 智东西 | zhidx.com | 登录弹窗干扰，标题提取需精细正则 |
| 量子位 | qbitai.com | HTTP 403 — CDN/WAF 防护 |
| 腾讯科技 AI | tech.qq.com/ai | JS 动态渲染 |
| 36氪 | 36kr.com | JS 渲染（已从来源列表移除） |
| 知乎 AI 话题 | zhihu.com | 复杂反爬机制，需登录 |
| Hugging Face Papers | huggingface.co/papers | HTML 结构复杂，可用但标题提取需要多 pattern 匹配 |
