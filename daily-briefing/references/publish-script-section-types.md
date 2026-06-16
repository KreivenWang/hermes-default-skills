# publish_article.py 排版类型参考

publish_article.py 的 `build_article_html()` 支持以下 section types。编写文章 JSON 时引用。

## 三色高亮语法

在 `text` 和 `collocation` 类型的 content 中可用：

| 语法 | 颜色 | 用途 |
|------|------|------|
| `**蓝色粗体**` | `#2563eb` 蓝色 | 核心数字或概念 |
| `==橙色高亮==` | `#d97706` 橙色 | 需要强调的差异点 |
| `~~紫色标注~~` | `#7c3aed` 紫色 | 易错点或特殊术语 |

## section types 一览

### text — 标准段落
```json
{"type": "text", "content": "正文内容，支持**蓝色** ==橙色== ~~紫色~~ 三色高亮"}
```
渲染：15px 字，1.75 行高，0.5px 字间距。自动处理换行 `\n` → `<br>`。

### heading — 章节标题
```json
{"type": "heading", "content": "英英释义"}
```
渲染：左侧 4px 蓝色竖条 + 18px 加粗标题。自动匹配 emoji：
- 英英释义 → 📖
- 中英释义 → 🌏
- 用法辨析 → 🔍
- 职场场景 → 💼
- 生活场景 → 🏠
- 常见搭配 → 🔗
- 小测试 → 📝
- 风险与挑战 → ⚠️
- 启示 → 💡
- 未匹配 → 📌

### subheading — 子标题
```json
{"type": "subheading", "content": "小节名称"}
```
渲染：蓝色小药丸（圆角背景）。

### comparison — ❌✅ 对比
```json
{"type": "comparison", "content": "❌ 中式错误用法\n\n✅ 地道表达方法"}
```
渲染：每行以 ❌/✗ 开头→红底红左框；以 ✅/✓ 开头→绿底绿左框。空行分隔两组对比。

### collocation — 搭配卡片
```json
{"type": "collocation", "content": "短语\n「中文释义」\n· 例句\n\n下一条短语\n「释义」\n· 例句"}
```
渲染：蓝色短语 + 灰色释义 + 例句。每条用双换行 `\n\n` 分隔。

### tip — 提示卡片
```json
{"type": "tip", "content": "一句话总结"}
```
渲染：💡 绿色边框卡片。

### warning — 警告卡片
```json
{"type": "warning", "content": "注意内容"}
```
渲染：⚠️ 黄色边框卡片。

### quote — 引用块
```json
{"type": "quote", "content": "引用的原文"}
```
渲染：灰色左竖线 + 斜体。

### list — 列表
```json
{"type": "list", "content": "第一项\n第二项\n第三项"}
```
渲染：圆点无序列表。

### quiz — 小测试
```json
{"type": "quiz", "content": "题干\nA. 选项A\nB. 选项B\nC. 选项C\nD. 选项D"}
```
渲染：紫色渐变卡片 + 底部 "🔒 答案下期公布" 标识。

### image — 指定位置插图
```json
{"type": "image"}
```
渲染：在此处插入下一张配图（按 image_sources 顺序）。不传 content。

### handwrite — 手绘风例句卡片
```json
{"type": "handwrite", "content": "I have the impression you worked at Google before.\n===我感觉你好像在谷歌工作过"}
```
渲染：Pillow 生成 700×200 PNG 图片（暖纸底色 `#FAF3E0` + Noteworthy 手写字体 + 粗糙边框 + 底部中文翻译）。`===` 前为英文主句，后为中文翻译。
注意：此段类型**会消耗一张 image_sources**（自动生成图片后追加到列表尾部）。

### divider — 分割线
```json
{"type": "divider"}
{"type": "divider", "content": "✦ ✦ ✦"}
```
渲染：居中灰色装饰字符。不传 content 时默认用 "✦ ✦ ✦"。

## 自动配图插入规则

1. 封面图：`image_sources` 第一张自动作为封面（居中展示）
2. 内文配图：每个 heading（首标题除外）自动插入一张
3. 正文 text：每 4 段自动插入一张
4. 手动 `{"type": "image"}`：在指定位置插入下一张
5. `{"type": "handwrite"}`：**自动生成手绘图片并消耗一张 image_sources 位置**
6. 如果 `image_sources` 耗尽，剩余自动插入位跳过

## 配图展示样式

所有配图直接以 `<img>` 标签渲染：
- **无外层 `<div>` 包裹**
- **无 `border-radius` / `box-shadow`**
- 仅 `margin:20px 0`（正文插图）或 `margin:0 0 22px`（封面图）
- 手写卡片自带的暖纸底色、粗糙边框和手写体由 Pillow 生成在图片内部
