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
- **提取方式**: 从 HTML 中 `<a href="..." title="...">` 提取，稳定
- **内容特点**: 深度 AI 报道，涵盖大模型、具身智能、智能体、CVPR 等
- **示例标题**: "复旦等提出 GuidedVLA，提升 VLA 可控可解释能力"
- **验证**: `curl -sL 'https://www.leiphone.com/category/ai' -A 'Mozilla/5.0' | python3 -c "import sys,re; [print(f'{m.group(1)} | {m.group(2)}') for m in re.finditer(r'<a[^>]*href=\"(https?://[^\"]+\.html)\"[^>]*title=\"([^\"]+)\"', sys.stdin.read())]"`

#### Ars Technica AI
- **URL**: arstechnica.com/ai
- **语言**: 英文
- **提取方式**: h2/h3 内的 `<a>` 链接提取，需拼接完整 URL
- **内容特点**: 深度技术报道，OpenAI、AI 政策、研究突破
- **示例标题**: "Chat is dead: OpenAI preps overhaul of ChatGPT"
- **验证**: `python3 scripts/fetch_sources.py | grep 'arstechnica' | head -3`

#### TechCrunch AI
- **URL**: techcrunch.com/category/artificial-intelligence
- **语言**: 英文
- **提取方式**: h2/h3 内的 `<a>` 链接提取
- **内容特点**: AI 创业公司、产品发布、融资动态
- **示例标题**: "OpenAI unveils Lockdown Mode to protect sensitive data from prompt injection"
- **注意**: 页面第一个链接是 logo，脚本已自动过滤

#### Wired AI
- **URL**: wired.com/category/artificial-intelligence
- **语言**: 英文
- **提取方式**: h2/h3 内的 `<a>` 链接提取，按 `/story/` 路径过滤
- **内容特点**: AI 趋势、评论、人物报道
- **示例标题**: "Databricks Has a Trick That Lets AI Models Improve Themselves"

#### BBC 科技
- **URL**: bbc.com/news/technology
- **语言**: 英文
- **提取方式**: Next.js 页面，先提取 `/news/articles/` 路径，再逐个请求 og:title
- **性能**: 每个 URL 耗时 2-3 秒（逐个请求获取标题）
- **示例标题**: "Apple and Google given three months to ban nude images on children's devices"
- **注意**: 部分文章可能偏向消费科技而非 AI，需筛选

#### arXiv AI RSS
- **URL**: arxiv.org/rss/cs.AI
- **语言**: 英文（论文）
- **提取方式**: XML RSS 稳定解析
- **内容特点**: 最新 AI 学术论文
- **示例标题**: "DiBS: Diffusion-Informed Branch Selection"
- **注意**: 论文较长较深，除非用户明确要论文板块，简报中慎用

### 需 web_search

#### The Verge AI
- **URL**: theverge.com/ai-artificial-intelligence
- **语言**: 英文
- **问题**: JS 渲染，curl 只能拿到骨架 HTML
- **替代**: 使用 web_search 搜索 "theverge.com AI" 或 "site:theverge.com artificial intelligence"

#### 机器之心
- **URL**: jiqizhixin.com
- **语言**: 中文
- **问题**: 页面结构复杂，curl 能拿到 HTML 但标题提取不可靠
- **替代**: 使用 web_search 搜索 "机器之心" 或相关关键词

---

## 国际（5 个 curl 可访问 + 3 个需 web_search）

### curl 可访问

#### AP News
- **URL**: apnews.com
- **语言**: 英文
- **提取方式**: h2/h3 内的 `<a>` 链接提取，按 `/article/` 或 `/live/` 路径过滤
- **内容特点**: 国际通讯社，覆盖全球重大新闻，140+ 链接
- **示例标题**: "Iranian military says it is halting offensive operations after Israel and Iran exchanged fire"
- **最佳实践**: 优先选取中东、亚太、欧洲等国际新闻，避免美国国内新闻

#### The Guardian
- **URL**: theguardian.com/international
- **语言**: 英文
- **提取方式**: h2/h3 内的 `<a>` 链接提取，按 `/2026/` 或 `/live/` 路径过滤
- **内容特点**: 英国视角的国际新闻，涵盖政治、经济、社会
- **示例标题**: "US-Israel war on Iran: exchange strikes as Middle East crisis threatens to escalate"
- **格式注意**: 标题可能前后粘着栏目名（如 "BusinessStock markets fall..."），脚本会提取原始标题

#### BBC
- **URL**: bbc.com/news
- **语言**: 英文
- **提取方式**: Next.js 嵌入数据，先提取 `/news/articles/` 路径，再逐个请求 og:title
- **性能**: 每个 URL 耗时 2-3 秒（逐个请求获取标题）
- **内容特点**: 全球新闻报道，稳定可靠
- **示例标题**: "Philippines: 32 dead after earthquake off Mindanao coast"

#### NPR
- **URL**: npr.org/sections/news
- **语言**: 英文
- **提取方式**: h2/h3 内的 `<a>` 链接提取，按 `/2026/` 路径过滤
- **内容特点**: 美国公共广播，国际新闻视角
- **示例标题**: "Xi and Kim express hopes for greater ties between China and North Korea"
- **注意**: 部分标题是栏目名称（如 "Up First Newsletter"），需过滤

#### SCMP（南华早报）
- **URL**: scmp.com/news
- **语言**: 英文
- **提取方式**: h2/h3 内的 `<a>` 链接提取
- **内容特点**: 亚洲视角国际新闻，香港/中国/亚太
- **示例标题**: "Russia & Central Asia"（部分标题是栏目名，需进一步筛选）
- **注意**: h2 标题多为栏目名而非文章标题，实际文章在 h3 中，条目较少

### 需 web_search

#### Reuters
- **URL**: reuters.com
- **语言**: 英文
- **问题**: JS 渲染 + 反爬，curl 返回 "Please enable JS and disable any ad blocker"
- **替代**: 使用 web_search 搜索 "reuters.com [topic]" 或 "site:reuters.com world"

#### Al Jazeera
- **URL**: aljazeera.com/news
- **语言**: 英文
- **问题**: JS 渲染，curl 拿不到内容
- **替代**: 使用 web_search 搜索 "aljazeera.com [topic]"

#### 财新
- **URL**: caixin.com
- **语言**: 中文
- **问题**: 需登录，curl 不可用
- **替代**: 使用 web_search 搜索 "财新 [topic]"

---

## 金融（3 个 curl 可访问 + 1 个需 web_search）

### curl 可访问

#### CNBC Markets
- **URL**: cnbc.com/markets
- **语言**: 英文
- **提取方式**: h2/h3 内的 `<a>` 链接提取，按 `/2026/` 路径过滤
- **内容特点**: 全球市场报道，含股票、商品、汇率
- **示例标题**: "Weight loss drug maker sinks 25% after new safety data spooks investors"
- **验证**: `python3 scripts/fetch_sources.py finance | grep 'cnbc' | head -3`

#### Business Insider Markets
- **URL**: businessinsider.com/markets
- **语言**: 英文
- **提取方式**: h2/h3 内的 `<a>` 链接提取，按 `/markets/` 或关键词过滤
- **内容特点**: 华尔街分析、市场评论、机构研报
- **示例标题**: "JPMorgan outlines how the S&P 500 can soar more than 20% in the next year"

#### Yahoo Finance
- **URL**: finance.yahoo.com
- **语言**: 英文
- **提取方式**: h2/h3 内的 `<a>` 链接提取，按 `/markets/` 或 `/articles/` 路径过滤
- **数量**: 通常 2-3 条可用，少于其他来源
- **示例标题**: "Wall St gains as chips rebound, Middle East tensions ease"

### 需 web_search

#### WSJ
- **URL**: wsj.com
- **语言**: 英文
- **问题**: 付费墙，curl 返回 401
- **替代**: 使用 web_search 搜索 "wsj.com [topic]"

---

## 抓取脚本用法

```bash
python3 scripts/fetch_sources.py                # 抓取全部
python3 scripts/fetch_sources.py ai             # 仅 AI
python3 scripts/fetch_sources.py intl           # 仅国际
python3 scripts/fetch_sources.py finance        # 仅金融
python3 scripts/fetch_sources.py list           # 列出所有来源
```

输出 JSON Lines，每行格式：
```json
{"title": "Article title", "url": "https://...", "source": "leiphone"}
```

---

## 来源筛选建议

### 保证"3条3个不同域名"的最佳组合

**AI**: leiphone（中文）+ arstechnica（英文深度）+ techcrunch（英文产品）→ 3 个不同域名 ✅
**备选**: wired / bbc-tech / arxiv（按需）

**国际**: apnews（通讯社）+ theguardian（英国）+ bbc（综合）→ 3 个不同域名 ✅
**备选**: npr / scmp

**金融**: cnbc（市场）+ businessinsider（分析）+ yahoo-finance（快讯）→ 3 个不同域名 ✅

### 脚本速度参考

| 来源 | 耗时 | 说明 |
|------|------|------|
| leiphone | ~2s | 单次 curl，正则直接提取 |
| arstechnica | ~2s | 单次 curl |
| techcrunch | ~2s | 单次 curl |
| wired | ~2s | 单次 curl |
| bbc/bbs-tech | ~8-10s | 先拉列表，再逐个请求标题 |
| apnews | ~2s | 单次 curl |
| guardian | ~2s | 单次 curl |
| npr | ~2s | 单次 curl |
| cnbc | ~2s | 单次 curl |
| businessinsider | ~2s | 单次 curl |
| **全量** | **~30-40s** | 全部来源并行约 30s |
