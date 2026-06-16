---
# 公众号文章 JSON 格式参考
# 用于 publish_article.py 的输入文件
---

## JSON 顶层字段

| 字段 | 类型 | 必填 | 说明 | 限制 |
|------|------|------|------|------|
| `date` | string | ✅ | 发文日期 | `YYYY-MM-DD` |
| `event_date` | string | ✅ | 事件发生日期 | `YYYY-MM-DD`，用户群发前填「事件发生日期」 |
| `title` | string | ✅ | 文章标题 | ≤ 64 字符 |
| `author` | string | ✅ | 作者名 | 固定为「简报」 |
| `digest` | string | ✅ | 摘要 | ≤ 100 字 |
| `sections` | array | ✅ | 文章正文段落 | 见下方 |
| `image_sources` | array | ✅ | 配图 URL 列表 | 必须是真实可访问的 URL |
| `source_links` | array | ✅ | 信息源列表 | 每条包含 source + url |

## sections 数组

每个元素结构：

```json
{"type": "text", "content": "正文段落"}
{"type": "heading", "content": "小标题"}
```

- `text` — 正文段落，支持 `**关键词**` 语法自动蓝色高亮
- `heading` — 小标题（显示为稍大字号加粗）

## source_links 数组

```json
[
  {"source": "TechCrunch", "url": "https://..."},
  {"source": "CNBC", "url": "https://..."}
]
```

- `source` — 来源平台名称，用于用户填「素材来源平台」
- `url` — 原文链接

## 完整示例

```json
{
  "date": "2026-06-13",
  "event_date": "2026-06-12",
  "title": "Mistral 估值翻倍冲200亿€",
  "author": "简报",
  "digest": "法国AI公司Mistral传出以200亿欧元估值融资30亿欧元...",
  "sections": [
    {"type": "text", "content": "第一段正文..."},
    {"type": "heading", "content": "小标题"},
    {"type": "text", "content": "支持 **高亮** 语法"}
  ],
  "image_sources": ["https://example.com/image.jpg"],
  "source_links": [
    {"source": "TechCrunch", "url": "https://techcrunch.com/..."}
  ]
}
```

## 常见错误

1. `JSONDecodeError` — 大概率是正文内残留 ASCII 双引号 `"`，改用 `「」`
2. 封面图 40007 — `image_sources` 里给了无效 URL，用 `curl -sL | grep og:image` 验证
3. 摘要 45004 — digest 超过 128 字符
