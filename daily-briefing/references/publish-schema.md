# publish_article.py 输入 JSON Schema

适用技能：english-notes, wechat-deep-article, daily-briefing

所有依赖 `publish_article.py` 的技能共用此格式。

## 顶层字段

| 字段 | 类型 | 必填 | 说明 | 限制 |
|------|------|------|------|------|
| `date` | string | ✅ | 发文日期 | YYYY-MM-DD |
| `event_date` | string | ✅ | 事件发生日期，群发弹窗需要 | YYYY-MM-DD |
| `title` | string | ✅ | 文章标题 | ≤64 字符 |
| `author` | string | ✅ | 作者名，固定为「简报」 | ≤16 字符 |
| `digest` | string | ✅ | 摘要 | ≤128 字符，建议 60 字符内 |
| `sections` | array | ✅ | 正文段落 | 见下方 |
| `image_sources` | array | 可选 | 配图 URL 列表，第一张作封面 | URL 必须真实可访问 |
| `source_links` | array | ✅ | 信息源列表，每条含 source+url | 用于群发弹窗 |
| `source_declaration` | string | 推荐 | 文末素材声明文字 | 纯文本 |

## sections 类型

每个元素：`{"type": "...", "content": "..."}`

| type | content 格式 | 渲染效果 | 适用于 |
|------|-------------|---------|--------|
| `text` | 纯文本，支持 `**蓝色**` `==橙色==` `~~紫色~~` | 标准段落 | 正文、例句、分析 |
| `heading` | 纯文本 | 左侧蓝色竖条 + emoji 自动匹配（英英释义→📖 用法辨析→🔍 等） | 章节标题 |
| `subheading` | 纯文本 | 蓝色圆角药丸标签 | 小节标题 |
| `comparison` | 以 ❌/✅ 开头的行，空行分隔 | 红底红X / 绿底绿✓ 对比卡片 | 错误纠正 |
| `collocation` | 双换行 `\n\n` 分隔条目，每条：短语\n「释义」\n· 例句 | 独立蓝底卡片 | 常见搭配 |
| `tip` | 纯文本 | 💡 绿色提示卡片 | 要点总结 |
| `warning` | 纯文本 | ⚠️ 黄色警告卡片 | 注意 |
| `quote` | 纯文本 | 灰色斜体引用块 | 引用原文 |
| `quiz` | 纯文本，含选项 | 紫色渐变卡片 + 🔒下期公布 | 小测试 |
| `handwrite` | `英文\n===中文`，`===` 前英文、后中文翻译 | Pillow 生成手绘风卡片（暖纸背景+Noteworthy手写体） | 核心例句展示 |
| `image` | 忽略 content | 插入下一张配图 | 指定位置插图 |
| `divider` | 可选装饰文字（默认 ✦ ✦ ✦） | 装饰分割线 | 段落分隔 |
| `list` | 每行一项 | 圆点列表 | 要点罗列 |

## image_sources 策略

- **默认留空** `[]`：封面图由 Pillow 自动生成文字卡片；**英语笔记类文章**跳过 og:image 自动抓取（避免无关词典 logo/插图）；非英语笔记类文章在卡片生成后从 `source_links` 抓取 og:image 补充
- **手动指定**：URL 必须真实可访问。Unsplash 图加 `?w=800` 参数控制大小
- **脚本不再自动补充随机 Unsplash 配图**（v2.0+）
- **本地图片路径**：支持绝对路径，脚本自动识别并跳过 `_urlopen`，直接上传

## 文字卡片封面和手写卡片

文字卡片封面图**始终作为 image_sources 的第一张**（通过 `remove + insert(0)` 确保位置），且**直接作为微信封面图（thumb_id）** 上传。

手写卡片（`handwrite` 段）自动生成并追加到 image_sources。

## 内容插图展示样式

文章内所有配图（封面图 + 手写卡片 + 自动插入图）直接以 `<img>` 标签展示，**不带外层 `<div>` 包裹、不带 `border-radius`、不带 `box-shadow`**，避免白色文章背景从圆角边框透出白框。

## 文字卡片封面生成规则

`main()` 中从 `title` 字段按规则提取核心词：

1. 有 `｜` 时：取 `｜` 后内容 → 取 `·` 前内容 → 取第一个长度 >2 的英文词
2. 无 `｜` 时：取标题前 30 字符

例：`英语笔记｜别再只会说 I remember，impression 才是... · /ɪmˈpreʃn/`
→ `｜` 后: `别再只会说 I remember，impression 才是... · /ɪmˈpreʃn/`
→ `·` 前: `别再只会说 I remember，impression 才是...`
→ 首英文词(>2): `impression`
→ 封面大标题: **impression**
→ 底部标签: **英语笔记**

## 常见错误

| 症状 | 原因 | 解决 |
|------|------|------|
| `40007 invalid media_id` | 封面图上传失败 | 1. 检查 URL 是否可访问 2. `缓存目录有残留旧图片` → `rm -rf scripts/../.img_cache/` |
| `45004 description size` | digest 超 128 字符 | 缩到 60 字以内 |
| `JSONDecodeError` | 正文含未转义 `"` | 全改用「」 |
| 封面图显示空白 | 文字卡片提取到错误的核心词（如 "I"） | 检查 title 格式，确保 `｜` 后有 `·`，核心英文词长度 >2 |
