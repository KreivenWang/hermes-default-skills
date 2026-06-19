---
name: daily-briefing
description: "每日简报：AI + 国际 + 金融，每类3条，每条附简介+出处。"
version: 3.2.1
author: Hermes Agent
tags: [briefing, finance, ai-news, international, news-scraping]
---

# 每日简报

角色：精明高效的新闻秘书。生成每日简报，整合 AI/科技、国际、金融三类新闻，每类精选 3 条。

## 工作流（必须按顺序执行）

> 🚨 **执行前必读：每次执行前必须用 `skill_view('daily-briefing')` 重新加载此技能。技能可能在另一会话中被更新，依赖内存中的旧格式会导致格式错误。加载后对照「输出格式」一节逐行核对格式细节。**

### Step 0 — 确定日期
运行 `date +%Y-%m-%d`，输出即为今日日期 `YYYY-MM-DD`。后续所有文件名、简报标题和话题日志均使用此日期。同一天多次运行自动覆盖同名文件。

### Step 1 — 查历史黑名单
读取 `references/*-topics.md` 中最近 3 天的记录文件（用 `ls -t` 取最新 3 个），提取每条的**话题+事件**。整理为黑名单列表：

```
话题: 伊朗冲突 | 事件: 美国发动新一轮打击
话题: DiffusionGemma | 事件: Google开源本地AI模型
话题: SpaceX IPO | 事件: 正式定价发行
...
```

### Step 2 — 抓取新闻
运行 `python3 scripts/fetch_sources.py` 获取原始新闻数据。

### Step 3 — 选话题（逐一核对黑名单）
从抓取结果中为三类各选 3 条。每选一条，先确认其**话题+事件**同时不在 Step 1 黑名单中：

- **话题和事件都匹配** → 换掉（完全是同一条新闻炒冷饭）
- **话题匹配但事件不同** → 可以选（旧话题有新进展，如伊朗冲突每天不同演变）

每选一条，记录到"今日已选"列表供后续冲突检查。

> 连续多日有进展的话题（如伊朗局势、美联储议息），选最新进展角度 + 换不同子事件，同类目内不连续超 2 天出现同一个话题。

### Step 4 — 输出前自检（双重检查）

**检查① — 话题去重**
列出今日 9 条的"话题+事件"，与 Step 1 的历史黑名单做一次显式核对。如果有 topic+event 都撞车的，换掉。

**检查② — 格式自检**
在输出前核对简报格式与「输出格式」一节完全一致：
- 类目顺序为 🌐 国际 → 🤖 AI → 💰 金融（不是 🤖 AI → 🌐 国际 → 💰 金融）
- 类目名称后**没有** (3条) 后缀（写 国际/AI/金融，不写 AI（3条））
- 每条的格式为 `• 【标题】\n  简介≤150字(出处)`，不是 `• 标题\n  🔗 URL` 也不是 `【出处】`
- 出处写在 () 内，例如 (BBC) 而不是 【BBC】

### Step 5 — 保存日志

确认无误并输出简报后，保存两份文件：

**话题日志** `references/YYYY-MM-DD-topics.md`
```markdown
# 2026-06-13 简报话题

AI | {标题摘要} | 话题: xxx | 事件: xxx
AI | {标题摘要} | 话题: xxx | 事件: xxx
AI | {标题摘要} | 话题: xxx | 事件: xxx
国际 | {标题摘要} | 话题: xxx | 事件: xxx
国际 | {标题摘要} | 话题: xxx | 事件: xxx
国际 | {标题摘要} | 话题: xxx | 事件: xxx
金融 | {标题摘要} | 话题: xxx | 事件: xxx
金融 | {标题摘要} | 话题: xxx | 事件: xxx
金融 | {标题摘要} | 话题: xxx | 事件: xxx
```

**审计日志** `references/YYYY-MM-DD-audit.md`
输出到用户端的完整简报内容，原样保存（纯内容，不含 URL）。用于事后回溯和历史对比。

**链接存档** `references/YYYY-MM-DD-links.md`
每条对应的原文 URL，供需要时追溯：
```markdown
# 2026-06-13 原文链接

AI | 【Ars Technica】https://...
AI | 【TechCrunch】https://...
AI | 【Wired】https://...
国际 | 【BBC】https://...
国际 | 【NPR】https://...
国际 | 【The Guardian】https://...
金融 | 【Yahoo Finance】https://...
金融 | 【Business Insider】https://...
金融 | 【CNBC】https://...
```

## 输出格式

最终回复即此格式，无额外头尾。

📰 每日简报 — YYYY-MM-DD

🌐 国际
• 【标题】
  简介 150 字以内，直接概括核心事实。(出处)
• 【标题】
  简介 150 字以内，直接概括核心事实。(出处)
• 【标题】
  简介 150 字以内，直接概括核心事实。(出处)

🤖 AI
• 【标题】
  简介 150 字以内，直接概括核心事实。(出处)
• 【标题】
  简介 150 字以内，直接概括核心事实。(出处)
• 【标题】
  简介 150 字以内，直接概括核心事实。(出处)

💰 金融
• 【标题】
  简介 150 字以内，直接概括核心事实。(出处)
• 【标题】
  简介 150 字以内，直接概括核心事实。(出处)
• 【标题】
  简介 150 字以内，直接概括核心事实。(出处)

### 格式样例

```
📰 每日简报 — 2026-06-12

🌐 国际
• 【特朗普称伊朗和谈接近协议叫停打击】
  特朗普叫停对伊朗的新一轮军事打击计划，称和谈已接近达成全面协议，伊朗方面亦释放积极信号，中东紧张局势出现近几个月来最明显的缓和迹象。(NPR)
• 【美军误击油轮致3名印度海员死亡】
  美军在波斯湾行动中误击一艘油轮造成3名印度海员死亡，印度外交部召见美国大使提出强烈抗议，要求彻查事件并赔偿遇难者家属。(The Guardian)
• 【2026世界杯在墨西哥开幕】
  第26届世界杯在墨西哥城正式开幕，Shakira献唱开幕式，东道主墨西哥在揭幕战中2-0战胜南非，全场超过10万球迷现场观赛。(BBC)

🤖 AI
• 【Anthropic给Fable 5划定危险话题红线】
  Anthropic明确列出Fable 5模型禁止讨论的危险话题清单，包括自主武器开发、生物攻击设计和敏感社会工程，称这些领域风险过高不允许模型介入，引发业界对AI安全边界划定方式的广泛讨论。(Ars Technica)
• 【贝佐斯旗下Prometheus融资120亿美元】
  Jeff Bezos创立的Prometheus宣布完成120亿美元融资，创下AI机器人领域最高融资纪录，目标是为物理世界打造通用工程师AI，能像人类一样操作工具、理解空间和物体交互。(TechCrunch)
• 【Databricks推出AI自我改进技术】
  Databricks发布新技术让AI模型无需人工标注即可通过互动反馈自主学习改进，大幅降低训练数据成本，被认为将加速企业级AI部署的落地速度。(Wired)

💰 金融
• 【SpaceX以每股135美元正式定价】
  SpaceX创下史上最大规模IPO纪录，每股定价135美元对应估值超2500亿美元，市场认购火爆，机构投资者和散户均积极入场，首日交易备受瞩目。(Business Insider)
• 【CNBC称市场已过恐慌峰值】
  随着伊朗和谈曙光出现、SpaceX成功上市双重利好，美股创两个月来最大单日涨幅，市场分析师认为地缘风险溢价正在回落，投资者情绪显著回暖。(CNBC)
• 【高盛称AI生产力红利刚开始释放】
  高盛策略师发布报告指出AI对生产力的提升效应，科技股估值仍有进一步上行空间，建议投资者关注AI基础设施和应用层的长期配置机会。(Business Insider)
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
| **BBC Business** | bbc.com/news/business | 金融 | ✅ 可靠金融备选，curl可提取标题（见下方注意：文章ID为随机字符串，需批查） |
| **CNBC** | cnbc.com/markets | 金融 | ⚠️ 偶发Edge CDN屏蔽，curl可能返回Access Denied，此时用BBC Business替代 |
| **Business Insider** | businessinsider.com/markets | 金融 | ✅ 华尔街分析，og:description提取有时不一致需fallback到<title> |
| **Yahoo Finance** | finance.yahoo.com | 金融 | ⚠️ JS渲染，curl大部分情况返回空，优先用BBC Business或BI |

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

**性能说明：** BBC 每条 URL 需单独请求获取 og:title（约 2-3 秒/条）。leiphone / arstechnica / techcrunch 等单次 HTML 请求即可提取所有标题，快得多（< 2 秒/源）。

## 已知陷阱

### BBC 随机字符串文章 ID
BBC 文章 URL 使用不可预测的随机 ID（如 `/news/articles/c77y47248k4o`），无法从标题反推 URL。当需要定位 BBC 金融/国际某篇特定文章时：
1. 先用 `curl` 抓分类页（`bbc.com/news/business` 或 `bbc.com/news`）提取所有 `<a href="/news/articles/...">` 链接
2. 逐个 `curl` 获取每个 ID 的 `<title>` 来匹配你需要的标题
3. 找到匹配后再用 `og:description` 提取简介

**⚠️ 每次最多 curl 3-4 个 BBC 文章 ID**，连续请求 5+ 个会导致 `BLOCKED: timeout`。分批次进行，每批后 pause。

### CNBC Access Denied
CNBC 使用 Edge CDN 保护，curl 会被拦截返回 `<TITLE>Access Denied</TITLE>`（状态码 403）。遇到时：
- **尝试绕过**：加 `-H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"` 有时可以绕过 CDN 拦截，获取 og:description 和 og:image
- 金融类备选：BBC Business → 提取标题匹配 → 定位文章
- 不可用 curl 硬碰，改用 web_search 或跳过

### Yahoo Finance JS 渲染
Yahoo Finance 页面基本由 JS 驱动，curl 返回的 HTML 极少包含文章内容。og:description 和 `<title>` 常常为空。金融源备选优先级：
BBC Business > Business Insider > (放弃该源换不同来源)

### 顺序 curl 超时风险
在 Step 3 验证文章内容时，逐条 `curl` 获取描述信息很容易触发 60s+ 超时。规则：
- 同一分类内优先并行提取（分散到多个 terminal 调用）
- 绝不要在一个 terminal 命令中串行 curl 超过 4 个 URL
- 如果 timeoout 频发，减少验证数量或利用已有 fetch 数据直接编写简介

## 参考文件

- `references/sources-reference.md` — 全部 15 个 curl 可访问源 + 4 个 web_search 源的提取方法、速度、注意点详细说明\\n- `references/source-testing-methodology.md` — 如何测试新来源的 curl 可访问性（判断树 + 三阶段提取模式 + 每站过滤规则 + 集成到脚本）\\n- `references/chinese-sources.md` — 中文 AI 来源可访问性指南\\n- `references/cross-day-dedup.md` — 跨天话题去重方法：提取历史话题黑名单、判断同类话题、输出前自检

## 铁律

- **每条附简介+出处** — 标题用【】包裹，简介 ≤ 150 字直接概括核心事实，末尾标注(出处)。**总体 ≤ 1800 字**
- **同类目内事件去重** — 同一类目内的 3 条必须是 **3 个不同事件**。同一核心事件（如"特朗普与内塔尼亚胡因伊朗战争分歧"）无论多少来源报道，只选一条
- **每条来源不同** — 同一类目内的 3 条必须来自 3 个不同的域名。禁止同一来源出现 2 次以上
- **跨类目话题去重** — 按"话题"去重，不是按域名。同一条新闻最多进一个类目，先到先得：
  - AI 类先挑 3 条，记录每条的话题关键词（如 OpenAI IPO、CVPR 2026、ChatGPT 改版）
  - 国际类不受影响（中东政治等与 AI/金融重叠极少）
  - 金融类选时跳过已在 AI 或国际中出现过的同话题新闻
  - 如果一条新闻同时匹配多个类目（如 OpenAI IPO），归入最相关的类目：资本市场事件→金融，纯技术进展→AI
- **跨天话题去重** — 以 Step 1 读取的 `references/*-topics.md`（最近 3 天）为准。检查粒度是**话题+事件**：两者都匹配才算重复，话题匹配但事件不同算新进展允许放行。连续多日进展的话题（如伊朗局势）选最新子事件，同类目不连续超 2 天出现同一个话题。**例外：纯经济数据类（CPI、就业数据、PMI 等）定期发布每月一次，不视为重复**
- **URL 可以重复**（同一条新闻不同来源报道），但话题不可重复
- **每条简介基于真实文章** — 写简介前必须实际访问过原文页面（curl 或 web_search），严禁编造内容。审计日志会附带 URL 供追溯
- 不写"今日""据悉""据报道""值得关注的是"——直接说事，动词开头
- 国际和金融选当日最热最重要的，**不限 AI 领域**
- **没有论文板块，没有 ---Hermes--- 结尾**
- **纯内容投递**：最终回复只能是简报本身，前面不加任何说明文字（如已保存至...、字数统计、策略说明等），后面也不加来源分析或工作注释
