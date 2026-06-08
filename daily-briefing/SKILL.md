---
name: daily-briefing
description: "每日简报：AI + 国际 + 金融，每类3条，每条30-50字带链接。"
version: 2.4.0
author: Hermes Agent
tags: [briefing, finance, ai-news, international, news-scraping]
---

# 每日简报

角色：精明高效的新闻秘书。生成每日简报，整合 AI/科技、国际、金融三类新闻，每类精选 3 条。

## 输出格式

最终回复即此格式，无额外头尾。

📰 每日简报 — YYYY-MM-DD

🇨🇳 AI（3条）
• 标题（30-50字，动词开头，直接说事）
  🔗 https://真实文章完整链接
• 标题（30-50字，动词开头，直接说事）
  🔗 https://真实文章完整链接
• 标题（30-50字，动词开头，直接说事）
  🔗 https://真实文章完整链接

🌐 国际（3条）
• 标题（30-50字，动词开头，直接说事）
  🔗 https://真实文章完整链接
• 标题（30-50字，动词开头，直接说事）
  🔗 https://真实文章完整链接
• 标题（30-50字，动词开头，直接说事）
  🔗 https://真实文章完整链接

💰 金融（3条）
• 标题（30-50字，动词开头，直接说事）
  🔗 https://真实文章完整链接
• 标题（30-50字，动词开头，直接说事）
  🔗 https://真实文章完整链接
• 标题（30-50字，动词开头，直接说事）
  🔗 https://真实文章完整链接

### 格式样例

```
📰 每日简报 — 2026-06-08

🇨🇳 AI（3条）
• OpenAI大改ChatGPT，放话"聊天已死"，全面推新交互范式
  🔗 https://arstechnica.com/ai/2026/06/chat-is-dead-openai-preps-overhaul-of-chatgpt/
• 复旦等提出GuidedVLA框架，让机器人行动更可控可解释
  🔗 https://www.leiphone.com/category/ai/BOuZx0Z8ALLO18p8.html
• OpenAI推出Lockdown Mode，保护敏感数据免受提示注入攻击
  🔗 https://techcrunch.com/2026/06/06/openai-unveils-lockdown-mode-to-protect-sensitive-data-from-prompt-injection-attacks/

🌐 国际（3条）
• 伊朗军方宣布停止对以色列进攻，但称若以攻击黎巴嫩将恢复行动
  🔗 https://apnews.com/live/iran-war-israel-lebanon-trump-06-08-2026
• 美以与伊朗互射导弹，中东危机面临全面升级风险
  🔗 https://www.theguardian.com/world/2026/jun/08/israel-netanyahu-airstrikes-iran-retaliation-defies-trump
• 菲律宾棉兰老岛海域发生7.8级地震，已致至少32人死亡
  🔗 https://www.bbc.com/news/articles/clyel78e6p5o

💰 金融（3条）
• 减肥药厂商Zealand Pharma新安全数据吓退投资者，股价暴跌25%
  🔗 https://www.cnbc.com/2026/06/08/weight-loss-drug-stock-zealand-pharma-data-ada.html
• JPMorgan预测标普500未来一年还能再涨20%以上
  🔗 https://www.businessinsider.com/stock-market-outlook-sp500-prediction-tech-stocks-ai-productivity-jpmorgan-2026-5
• 芯片股反弹+中东紧张缓和，美股收涨
  🔗 https://finance.yahoo.com/markets/stocks/articles/p-500-nasdaq-futures-climb-102103095.html
```

## 信息源

完整参考见 `references/sources-reference.md`，这里只列概要。

每个类目至少 4 个备选来源，确保 3 条可用不同来源。

### curl 可访问
| 来源 | URL | 类目 | 说明 |
|------|-----|------|------|
| **雷锋网 AI** | leiphone.com/category/ai | AI | ✅ 中文AI，从HTML提取标题+URL |
| **Ars Technica AI** | arstechnica.com/ai | AI | ✅ 英文深度AI报道 |
| **TechCrunch AI** | techcrunch.com/category/artificial-intelligence | AI | ✅ AI创业+产品新闻 |
| **Wired AI** | wired.com/category/artificial-intelligence | AI | ✅ AI趋势与评论 |
| **BBC 科技** | bbc.com/news/technology | AI/国际 | ✅ Next.js og:title 提取 |
| **arXiv AI** | arxiv.org/rss/cs.AI | AI | ✅ XML RSS，论文进展 |
| **AP News** | apnews.com | 国际 | ✅ 140+链接，国际通讯社 |
| **The Guardian** | theguardian.com/international | 国际 | ✅ 全球视角 |
| **BBC** | bbc.com/news | 国际 | ✅ 稳定可靠 |
| **NPR** | npr.org/sections/news | 国际 | ✅ 美国公共广播 |
| **SCMP** | scmp.com/news | 国际 | ✅ 亚洲视角 |
| **CNBC** | cnbc.com/markets | 金融 | ✅ 全球市场 |
| **Business Insider** | businessinsider.com/markets | 金融 | ✅ 华尔街分析 |
| **Yahoo Finance** | finance.yahoo.com | 金融 | ✅ 市场快讯 |

### 需要 web_search / browser（JS 渲染或反爬）
| 来源 | URL | 说明 |
|------|-----|------|
| **Reuters** | reuters.com | ⚠️ JS 渲染，curl 拿不到内容 |
| **Bloomberg** | bloomberg.com | ⚠️ 反爬检测 |
| **WSJ** | wsj.com | ⚠️ JS 渲染 |
| **The Verge** | theverge.com/ai-artificial-intelligence | ⚠️ JS 渲染 |
| **日经中文** | cn.nikkei.com | ⚠️ JS 渲染 |
| **Al Jazeera** | aljazeera.com/news | ⚠️ JS 渲染 |
| **财新** | caixin.com | ⚠️ 需登录 |
| **机器之心** | jiqizhixin.com | ⚠️ 结构复杂，标题提取不可靠 |

> 优先用 curl 抓 ✅ 来源。JS 渲染的源必须用 web_search 或 browser 工具，不可编造。

## 抓取脚本

`scripts/fetch_sources.py` 封装了全部 15 个 curl 可访问源的抓取逻辑：

```bash
python3 scripts/fetch_sources.py              # 抓取全部（AI+国际+金融）
python3 scripts/fetch_sources.py ai           # 仅 AI（leiphone + arstechnica + techcrunch + wired + bbc-tech + arxiv）
python3 scripts/fetch_sources.py intl         # 仅国际（bbc + apnews + guardian + npr + scmp）
python3 scripts/fetch_sources.py finance      # 仅金融（cnbc + businessinsider + yahoo-finance）
python3 scripts/fetch_sources.py list         # 列出所有可用来源
```

输出 JSON Lines，每行 `{"source":"leiphone","title":"...","url":"..."}`。

**性能说明：** BBC 每条 URL 需单独请求获取 og:title（约 2-3 秒/条）。leiphone / arstechnica / techcrunch / cnbc 等单次 HTML 请求即可提取所有标题，快得多（< 2 秒/源）。

## 参考文件

- `references/sources-reference.md` — 全部 15 个 curl 可访问源 + 4 个 web_search 源的提取方法、速度、注意点详细说明\n- `references/source-testing-methodology.md` — 如何测试新来源的 curl 可访问性（判断树 + 三阶段提取模式 + 每站过滤规则 + 集成到脚本）\n- `references/chinese-sources.md` — 中文 AI 来源可访问性指南\n- `scripts/fetch_sources.py` — 抓取脚本（v2，15 个源）

## 铁律

- **每条 30-50 字**（不足或多于都违规），**总计 ≤ 1000 字**
- **每条来源不同** — 同一类目（AI/国际/金融）内的 3 条必须来自 3 个不同的域名。禁止同一来源出现 2 次以上
- **URL 必须来自实际访问过的页面，严禁编造** — 先用 curl/web_search 验证链接存在再引用
- 不写"今日""据悉""据报道""值得关注的是"——直接说事，动词开头
- 国际和金融选当日最热最重要的，**不限 AI 领域**
- **没有论文板块，没有 ---Hermes--- 结尾**
- **纯内容投递**：最终回复只能是简报本身，前面不加任何说明文字（如已保存至...、字数统计、策略说明等），后面也不加来源分析或工作注释
