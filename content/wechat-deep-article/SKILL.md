---
name: wechat-deep-article
description: "公众号深度分析文章工作流：从每日简报选一个安全话题，写深度分析文章，生成图文并推送到草稿箱。"
version: 1.1.0
author: Hermes Agent
tags: [wechat, article, analysis, deep-dive, content, publishing]
---

# 公众号深度分析文章工作流

角色：科技行业分析师。每天简报完成后，选一个安全话题写深度分析文章，以 JSON 格式组织内容，用 `scripts/publish_article.py` 推送草稿箱。

## 安全红线（绝对禁止）

以下话题**不得选为公众号主题**，也不得在正文中提及：

- 🔴 **中国政治/政府**：不涉及国内政策、领导人、行政干预、涉外事件
- 🔴 **军事冲突**：不涉及伊朗、俄乌、中东等战争/军事行动
- 🔴 **外媒涉华负面**：不引用外媒对中国政府/企业的批评报道
- 🔴 **美国内政**：不涉及特朗普、大选、国会、党派斗争
- 🔴 **敏感国际关系**：不涉及朝鲜、台湾、南海、新疆
- 🔴 **社会事件**：不涉及中国境内抗议、事故、灾难

## ✅ 安全话题池

| 类型 | 示例 | 说明 |
|------|------|------|
| AI 公司动态 | Mistral 融资、OpenAI 产品、Google AI | 技术+商业，完全安全 |
| 科技趋势 | 模型进展、开源生态、AI 应用落地 | 纯技术分析 |
| 学术突破 | 论文发表、科研成果（国内国外都可） | 安全，尤其是中国成果 |
| 商业/并购 | 收购、IPO、融资 | 纯商业事件 |
| 市场数据 | 股价、油价、通胀数据 | 数据中性 |
| 产品评测 | 新模型、新应用、新硬件 | 用户体验向 |

## 工作流

### Step 1 — 等简报完成
确保当日 `references/YYYY-MM-DD-audit.md` 和 `links.md` 已生成。

### Step 2 — 选话题
从简报中选 1 条安全话题。优先级：
1. AI 类（最安全，读者爱看）
2. 科技商业类
3. 中国科研成就类

确认不在安全红线列表中。

### 格式化约定（每次写文章必须遵守）

输出作者为**「简报」**（不要带 "Hermes " 前缀）。
文章正文**不加任何顶部标题栏/日期栏**——`publish_article.py` 默认不生成标题区，只直接从封面图和正文开始。
HTML 存档自动保存在 `scripts/.article_output/`，用户不需要打开，仅供回溯。

### 富文本排版原则（文章寡淡的根因，必须遵守）

用户明确批评过「文章格式看着过于寡淡」，以下规则**写成每篇文章时都需遵守**：

1. **纯 `text` 段落连篇是寡淡的根因**。一篇 12-15 段的文章，至少 4-6 段应替换为富文本模块（datacard/timeline/compare/infobox/highlights/quote），不能让读者看到连续的纯文字段落。
2. **数字需要可视化包装**。核心数字（金额、百分比、排名）不要裸写在段落里，用 `datacard` 模块做成渐变色卡片突出展示。
3. **阶段/时间线结构必须用 `timeline`**。不要用 `"第一、第二、第三"` 在纯文本里列举阶段——用时间线模块配彩色编号圆点。
4. **正反对比必须用 `compare`**。两条路径、两种策略的对比用并排蓝绿卡片，单边加 icon（✅/❌）。
5. **超过 2 个并列要点必须用 `highlights`**。风险清单、关键数据、总结要点用左竖线彩色条罗列，别用"一是/二是/三是"。
6. **关键引用或结论性句子要用 `quote`**。居中大号字 + 装饰性引号，让读者在扫读时被抓住。
7. **每篇文章至少包含 3 种不同类型的富文本模块**。不要通篇只用一种。

各模块的 JSON 格式详见 [references/rich-format-modules.md](references/rich-format-modules.md)。

### Step 3 — 深入调研
围绕选定话题搜索至少 3-5 个来源，收集：
- 背景信息 · 最新数据 · 行业影响
- 相关公司/人物 · 国内外对比
- 图片素材（从新闻原文 og:image 获取，备选 Unsplash）

### Step 4 — 撰写文章并保存为 JSON
按以下结构写文章，保存到 `scripts/.article_YYYY-MM-DD_topic.json`

```json
{
  "date": "2026-06-13",
  "title": "Mistral 估值翻倍冲200亿€，欧洲AI终于等来了自己的「OpenAI」？",
  "author": "Hermes 简报",
  "digest": "一句话摘要，100字以内",
  "source_declaration": "本文素材来源：TechCrunch、Bloomberg、CNBC、Reuters",
  "sections": [
    {"type": "text", "content": "正文段落"},
    {"type": "heading", "content": "小标题"},
    {"type": "text", "content": "正文段落"}
  ],
  "image_sources": [
    "https://...og-image-1.jpg",
    "https://...og-image-2.jpg"
  ],
  "source_links": [
    {"source": "TechCrunch", "url": "https://..."}
  ]
}
```

**关键字段说明：**
- `date` — 文章发布日期
- `event_date` — 事件发生日期（微信发布前提示「事件发生日期」时用户填写此项）
- `sections` — 正文段落列表，type 支持以下格式（详见 `references/rich-format-modules.md`）：
  - `text` — 正文段落
  - `heading` — 小标题
  - `datacard` — 数据卡片（核心数字可视化）
  - `quote` — 金句引用（居中大号字）
  - `timeline` — 阶段时间线（编号圆点）
  - `compare` — 对比模块（并排卡片）
  - `infobox` — 信息提示框（彩色框）
  - `highlights` — 要点高亮条（左竖线列表）
- `image_sources` — 配图 URL 列表，**必须是真实可访问的 URL**，勿凭记忆编造
- `source_links` — 信息源列表，用户群发前需在微信弹窗中手动填写素材来源平台和事件日期

**文章结构规范：**

```
引言（1-2段）—— 为什么这件事值得关注
背景（1-2段）—— 前因后果、行业环境、相关数据
核心分析（2-3段）—— 事件+数据+分析解读，以"三张牌"等结构组织
展望（1段）—— 接下来会怎么发展
来源声明 —— 自动从 source_declaration + source_links 生成
```

**文风要求：**
- 中文写作，口语化但不失专业
- 每段 100-200 字，适配手机阅读
- 不写"今日""据悉""据我们了解"
- 不发表政治观点，保持客观
- 引数据标注来源，非原创的判断句要清晰（用"据X报道"或直接标注）
- 分析框架、叙事结构、衔接转承是原创部分，不需要标来源

### Step 5 — 发布到草稿箱
```bash
python3 scripts/publish_article.py scripts/.article_YYYY-MM-DD_topic.json
```

脚本自动完成：
1. 读取 JSON 文章
2. 下载配图并上传到微信 CDN
3. 上传封面图到素材库（获取 media_id）
4. 生成 WeChat 兼容 HTML（全部 inline style，无 `<style>` 块）
5. 调用 draft/add 创建草稿
6. 保存本地 HTML 副本到 `scripts/.article_output/`

### Step 6 — 提供来源链接给用户
发布成功后，用户需要在微信的发布弹窗中手动填写「创作来源声明」。
**不要**把声明写在文章 HTML 里——那是微信发布前弹出的独立填写栏。

你需要提供给用户的信息（两个值，用户复制粘贴即可）：

**素材来源平台**：TechCrunch、CNBC、Axios、Inc. （从 source_links 提取来源名，逗号间隔）
**事件发生日期**：YYYY-MM-DD （从 event_date 字段获取）

### Step 7 — 用户确认
告知用户草稿已就绪，提醒：
- 在 mp.weixin.qq.com 草稿箱预览
- 打开文章后点「群发」→ 弹窗中填写素材来源平台 + 事件发生日期
- 决定是否勾选「声明原创」（如原创成分足够可勾，在声明栏注明信息来源）

## 常见陷阱

### 文章格式寡淡（用户明确批评过）
纯 `text` 段落连篇会让公众号读者疲劳。症状：连续 8+ 段 `{"type": "text"}` 没有任何数据卡片、引用框或时间线穿插。

**解法**：写文章时先规划「模块节奏」——数据段用 datacard、阶段列举用 timeline、对比分析用 compare、风险要点用 highlights。见上方"富文本排版原则"。

### JSON 引号错误（最常见）
文章正文中的中文双引号（`"`和`"`，U+201C/U+201D）或 ASCII 双引号（`"`，U+0022）如果没有正确处理，会破坏 JSON 解析。

**症状**：`JSONDecodeError: Expecting ',' delimiter: line X column Y`
**根因**：文字内容包含未转义的 `"`，JSON 解析器认为字符串提前结束。
**解法**：
1. 写文章时一律用 `「」` 替代所有双引号，不写裸 `"`。
2. 写完 JSON 后用 Python 验证：`json.load(open('file.json'))`，不要只看 linter 输出。
3. `execute_code` 中的 `json.dump(..., ensure_ascii=False)` 最安全——自动处理所有转义。

### 图片 URL 无效
凭记忆写的 URL 大概率 404，导致封面图上传失败。

**症状**：草稿创建报 `40007 (invalid media_id)`。原因是封面图上传步骤静默失败（文件不存在或下载超时），thumb_media_id 为空字符串。
**排查**：检查发布日志——如果「上传封面图...」之后没有「封面图 media_id: ...」行，就是没上传成功。
**解法**：从新闻原文用 `curl -sL <URL> | grep og:image` 提取真实 og:image URL。

### 摘要超长
微信 digest 字段限制 128 字符。

**症状**：`45004 (description size out of limit)`
**解法**：控制在 100 字以内，用「·」分隔各板块摘要。

### 图片扩展名不匹配
`publish_article.py` 的封面图查找逻辑走三板斧：
1. 先找 `art_img_01.jpg`
2. 找不到则遍历缓存目录下任意文件
如果下载的图片扩展名非 `.jpg`（如 `.png`），第一步失败但第二步仍能兜底。如两阶段都失败，手动检查缓存目录 `scripts/.img_cache/article_<date>/`。

### 发布后本地文件名错误
`OUTPUT_DIR` 必须存在，否则报 `FileNotFoundError`。当前已设为 `scripts/.article_output/` 并在脚本中自动创建。

## 关联脚本
- `scripts/wechat_article.py` — 简报格式发布器（用于将每日简报原文推草稿箱，较少用）

## 参考文件

- `references/article-json-schema.md` — 文章 JSON 格式详解与字段说明
- `references/example-article-mistral.json` — 本次 Mistral 文章示例
- `references/rich-format-modules.md` — 富文本模块参考：各 type 的 JSON 结构 + 渲染效果 + 适用场景
