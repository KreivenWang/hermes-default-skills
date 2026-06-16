# 富文本模块参考

## 总则

`publish_article.py` 的 `build_article_html()` 支持以下 section type。写文章时按「模块节奏」穿插使用，避免纯 text 段落连篇。

---

## 1️⃣ datacard — 数据卡片

**场景**：核心数字可视化（金额、百分比、排名、关键指标）

**JSON 结构**：
```json
{"type": "datacard", "items": [
  {"value": "220亿", "label": "收购价（美元）", "color": "purple"},
  {"value": "-17%", "label": "Fox股价日跌幅", "color": "red"},
  {"value": "#3", "label": "美国家庭覆盖率", "color": "blue"}
]}
```

**color 取值**：`purple` / `red` / `blue` / `green` / `orange` / `teal`
每色对应一组渐变色。

**注意**：data-items 最多 4 个，2-3 个视觉效果最佳。超过 4 个改用 highlights。

---

## 2️⃣ quote — 金句引用

**场景**：关键观点、核心结论、有冲击力的判断句
**原则**：全文最多 2 处 quote，用多了反而降级

**JSON 结构**：
```json
{"type": "quote", "content": "内容趋同之后，竞争壁垒从「你买不买得起IP」变成了「观众在哪儿打开电视」"}
```

**渲染**：
- 居中大号字 (16px, font-weight:500)
- 上下装饰性引号 (U+201C/U+201D)
- 底部渐变分割线
- 浅灰背景，13px 内边距

---

## 3️⃣ timeline — 阶段时间线

**场景**：行业三阶段、公司历程、产品迭代路线
**原则**：3-5 个阶段最佳，每个阶段 title 简短（≤12 字）

**JSON 结构**：
```json
{"type": "timeline", "items": [
  {"phase": "1", "title": "2015-2020 · 内容军备赛", "desc": "Netflix 年烧 150 亿美元做原创"},
  {"phase": "2", "title": "2020-2024 · 盈利大考", "desc": "广告套餐、密码打击、合并潮"},
  {"phase": "3", "title": "2025+ · 平台争夺战", "desc": "谁控制首页，谁拥有推荐权和广告位"}
]}
```

**渲染**：
- 左竖线连接（渐变颜色）
- 彩色编号圆点
- 阶段 title 与编号颜色匹配
- desc 灰色 14px

---

## 4️⃣ compare — 对比模块

**场景**：两条路径对比、正反观点、新旧模式对比
**原则**：只支持两侧对比，不要做三栏对比

**JSON 结构**：
```json
{"type": "compare", "sides": [
  {
    "icon": "❌",
    "title": "Disney 路径",
    "points": ["自建技术栈 BAMTech", "技术成本上吃尽苦头"],
    "color": "blue"
  },
  {
    "icon": "✅",
    "title": "Fox 路径",
    "points": ["直接买下行业#1平台", "$220亿全款拿下"],
    "color": "green"
  }
]}
```

**color 取值**：`blue` / `green` / `red` / `orange`
**icon 建议**：❌/✅ 或 左/右箭头

---

## 5️⃣ infobox — 信息提示框

**场景**：补充说明、关键数据、注意事项、引述来源

**style 取值**：
- `info`（蓝色）— 常规补充信息
- `warning`（橙色）— 风险提示
- `tip`（绿色）— 关键数据/正面信息

**JSON 结构**：
```json
{"type": "infobox", "style": "info", "title": "📎 协同效应", "content": "Lachlan Murdoch 称这笔收购每年可产生约 4 亿美元协同效应。不过每年 4 亿在 220 亿面前，ROI 并不高。"}
```

同一 Style 的 infobox 可以在一篇文章中出现多次（不同话题）。
相邻的两个 infobox 自动加上边距 (8px)。

---

## 6️⃣ highlights — 要点高亮条

**场景**：风险清单、关键要点、总结归纳
**原则**：3-5 条最佳，每条内容控制在 20 字内

**JSON 结构**：
```json
{"type": "highlights", "items": [
  {"title": "风险一", "content": "收购溢价 32-37%，代价不低", "color": "purple"},
  {"title": "风险二", "content": "120亿过桥贷款，杠杆 2.8x", "color": "red"},
  {"title": "风险三", "content": "媒体与科技文化整合挑战", "color": "blue"}
]}
```

**color 取值**：`purple` / `red` / `blue` / `green` / `orange`

**渲染**：
- 浅灰底 + 左竖线颜色与 color 匹配
- title 作为标签小字加粗
- content 正文

---

## 模块编排建议

一篇 12-15 段文章的理想模块节奏：

```
引言 (text)
数据卡片 (datacard)          ← 前三段内必插
背景段落 (text)
金句 (quote)                 ← 一次冲击
背景段落 (text)
阶段时间线 (timeline)         ← 替代"第一/第二/第三"文字
核心分析 (text)
对比 (compare)               ← 正反观点
要点清单 (highlights)         ← 风险/关键数据
信息框 (infobox)              ← 补充细节
展望段落 (text)
```

每篇文章必须包含**至少 3 种不同类型**的富文本模块。
