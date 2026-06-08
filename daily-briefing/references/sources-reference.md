# 每日简报 — 来源总表

## 概览

共 19 个来源（15 个 curl 可访问 + 4 个需 web_search），覆盖 AI、国际、金融三大类。

curl 可访问的来源可用脚本 `scripts/fetch_sources.py` 一键抓取。
需 web_search 的来源在 prompt 中指示 agent 用 web_search 或 browser 工具获取。

---

## AI / 科技（6 个 curl 可访问 + 2 个需 web_search）

### curl 可访问

#### 雷锋网 AI
- **URL**: leiphone.com/category/ai
- **语言**: 中文
- **提取方式**: 从 HTML 中 `<a href="..." title="...">` 提取
- **内容特点**: 深度 AI 报道，涵盖大模型、具身智能、智能体、CVPR 等
- **示例标题**: "复旦等提出 GuidedVLA，提升 VLA 可控可解释能力"
- **验收命令**: `python3 scripts/fetch_sources.py | python3 -c "import sys,json;[print(json.loads(l)['title'][:60]) for l in sys.stdin if 'leiphone' in l]" | head -3`

#### Ars Technica AI
- **URL**: arstechnica.com/ai
- **语言**: 英文
- **提取方式**: h2/h3 内的 `<a>` 链接提取
- **内容特点**: 深度技术报道，OpenAI、AI 政策、研究突破
- **验收命令**: `python3 scripts/fetch_sources.py ai | python3 -c "import sys,json;[print(json.loads(l)['title'][:60]) for l in sys.stdin if 'arstechnica' in l]" | head -3`

#### TechCrunch AI
- **URL**: techcrunch.com/category/artificial-intelligence
- **语言**: 英文
- **提取方式**: h2/h3 内的 `<a>` 链接提取（页面第一个链接是 logo，脚本已过滤）
- **内容特点**: AI 创业、产品发布、融资动态

#### Wired AI
- **URL**: wired.com/category/artificial-intelligence
- **语言**: 英文
- **提取方式**: h2/h3 内的 `<a>` 链接，按 `/story/` 路径过滤
- **内容特点**: AI 趋势、评论、人物报道

#### BBC 科技
- **URL**: bbc.com/news/technology
- **语言**: 英文
- **提取方式**: Next.js 页面，先提取 `/news/articles/` 路径，再逐个请求 og:title
- **性能**: ~2-3 秒/条（逐个请求），在 fetch_sources.py 中调优过

#### arXiv AI RSS
- **URL**: arxiv.org/rss/cs.AI
- **语言**: 英文（论文）
- **提取方式**: XML RSS，`xml.etree.ElementTree` 解析
- **注意**: 论文较长，除非用户明确要论文板块，简报中慎用

### 需 web_search

#### The Verge AI
- **URL**: theverge.com/ai-artificial-intelligence
- **问题**: JS 渲染
- **替代**: `web_search search "site:theverge.com artificial intelligence"`

#### 机器之心
- **URL**: jiqizhixin.com
- **问题**: 结构复杂，标题提取不可靠
- **替代**: `web_search search "机器之心 [topic]"`

---

## 国际（5 个 curl 可访问 + 3 个需 web_search）

### curl 可访问

#### AP News
- **URL**: apnews.com
- **语言**: 英文
- **提取方式**: h2/h3 提取后按 `/article/` 或 `/live/` 路径过滤
- **特点**: 140+ 链接，国际通讯社，最佳国际来源

#### The Guardian
- **URL**: theguardian.com/international
- **语言**: 英文
- **提取方式**: h2/h3 提取后按 `/2026/` 或 `/live/` 过滤
- **特点**: 英国视角国际新闻

#### BBC
- **URL**: bbc.com/news
- **语言**: 英文
- **提取方式**: Next.js og:title

#### NPR
- **URL**: npr.org/sections/news
- **语言**: 英文
- **提取方式**: h2/h3 按 `/2026/` 过滤

#### SCMP
- **URL**: scmp.com/news
- **语言**: 英文
- **提取方式**: h2/h3 按 `/news/` 过滤，排除 module= 类目页
- **注意**: h2 多为类目名，实际文章在 h3，条目较少

### 需 web_search

#### Reuters / Al Jazeera / 财新
- 均 JS 渲染或需登录，用 `web_search` 替代

---

## 金融（3 个 curl 可访问 + 1 个需 web_search）

### curl 可访问

#### CNBC Markets
- **URL**: cnbc.com/markets
- **语言**: 英文
- **提取**: h2/h3 按 `/2026/` 过滤
- **特点**: 全球市场、股票、商品、汇率

#### Business Insider Markets
- **URL**: businessinsider.com/markets
- **语言**: 英文
- **提取**: h2/h3 按 `/markets/` 或 `/stock-market-` 或 `/spacex-` 过滤

#### Yahoo Finance
- **URL**: finance.yahoo.com
- **语言**: 英文
- **提取**: h2/h3 按 `/markets/` 或 `/articles/` 过滤

### 需 web_search

#### WSJ
- **URL**: wsj.com
- **问题**: 付费墙 401
- **替代**: `web_search search "site:wsj.com [topic]"`

---

## 抓取脚本用法

```bash
python3 scripts/fetch_sources.py              # 全部
python3 scripts/fetch_sources.py ai           # AI
python3 scripts/fetch_sources.py intl         # 国际
python3 scripts/fetch_sources.py finance      # 金融
python3 scripts/fetch_sources.py list         # 列出来源
```

输出 JSON Lines: `{"title":"...","url":"...","source":"..."}`

## "3条3个不同域名"最佳组合

| 类目 | 推荐组合 | 域名 |
|------|---------|------|
| AI | leiphone + arstechnica + techcrunch | 3 ✅ |
| 国际 | apnews + theguardian + bbc | 3 ✅ |
| 金融 | cnbc + businessinsider + yahoo-finance | 3 ✅ |

## 脚本速度参考

| 来源 | 耗时 | 原因 |
|------|------|------|
| leiphone / arstechnica / techcrunch / wired / apnews / guardian / npr / cnbc / businessinsider / yahoo-finance | ~2s | 单次 curl + 正则 |
| bbc / bbc-tech | ~8-10s | 先拉列表再逐个请求 og:title |
| arxiv | ~2s | XML RSS |
| **全量** | ~30-40s | 全部 15 个源 |
