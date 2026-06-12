---
name: exam-countdown-briefing
description: "考试倒计时：当用户询问考试倒计时时，立即用 Python 计算剩余天数并生成倒计时简报。也支持设置 cron 定时推送。"
version: 2.0.0
created_by: agent
tags: [cron, briefing, exam, countdown, wechat, motivation, on-demand]
---

# 考试倒计时

**核心行为：用户一提"考试倒计时"或类似关键词，立即执行以下步骤生成输出，不得只给说明文档。**

已知考试信息（来自历史对话）：
- 考试：中级会计
- 日期：2026-09-05
- 领域：财务/会计

若用户未提供考试名称和日期，先问清楚再生成。

## 即时生成步骤

### 1. 计算天数

用 Python 或 shell `date` 命令获取今天日期，计算距考试日的天数差。

### 2. 判断阶段

| 剩余天数 | 阶段标签 | 语气 |
|----------|----------|------|
| > 60 | 备考筑基期 | 温和坚定，厚积薄发，底层逻辑构建 |
| 30–60 | 冲刺瓶颈期 | 心理疏导，抗压，查漏补缺 |
| 14–30 | 强化突破期 | 聚焦高频考点，针对性突破 |
| < 14 | 考前决战期 | 热血果断，极简有力 |

### 3. 生成行内段子

完整的会计术语库见 `references/accounting-domain-jargon.md`（80+ 术语 + 分阶段例句 + 通用段子）。

核心术语池：资产负债表、借贷平衡、试算平衡、会计分录、固定资产、无形资产、存货、应收账款、公允价值、减值、短期借款、应付账款、预计负债、营业收入、营业成本、管理费用、合并报表、非货币性资产交换、债务重组、会计政策变更、前期差错更正、在建工程、商誉、实收资本、资本公积、坏账准备、经营现金流

**铁律：** 每句段子必须包含至少一个会计术语，不准用"只要努力就能成功"等空话。

### 4. 输出格式（最终回复即此格式，无额外头尾）

📚 {考试名称} 倒计时
——————
⏰ 距考试：{X} 天 【{阶段标签}】
📅 {YYYY-MM-DD}

💡 今日财会心法：
{会计术语段子，≤50字}

🔥 倾力助攻：
{阶段匹配的鼓励语，含会计术语，≤60字}

——————
📌 备考提示：{一句话建议}

---

## 设置 Cron 定时推送（仅当用户明确要求时）

> 以下内容为参考，用户没提要 cron 就不要主动创建 cron job。

### 步骤 1：收集参数

Ask or extract:
- **Exam name** (e.g., 会计中级职称 / CFA Level 1 / 法考)
- **Exam date** (e.g., 2026-09-12)
- **Delivery time** (default: 9:00 AM)
- **Delivery platform** (default: check user's configured WeChat/Telegram/etc.)
- **Domain/industry** (for generating domain-specific wisdom — accounting, law, tech, medical, etc.)
- **Character limit** (default: 400 for WeChat mobile, 1000 for Telegram/CLI)

### 2. Calculate Phase Thresholds

Use shell `date` to get today's date, then compare to exam date. Define phases:

| Days remaining | Phase label | Tone |
|----------------|-------------|------|
| > 60 | 备考筑基期 | 温和坚定，厚积薄发，底层逻辑构建 |
| 30–60 | 冲刺瓶颈期 | 心理疏导，抗压，查漏补缺 |
| 14–30 | 强化突破期 | 聚焦高频考点，针对性突破 |
| < 14 | 考前决战期 | 热血果断，极简有力，唤醒肌肉记忆 |

### 3. Generate Domain-Specific Wisdom

完整的会计术语映射见 `references/accounting-domain-jargon.md`。各行业语料池：

| Domain | Jargon pool |
|--------|-------------|
| 财务/会计 | 资产负债表、借贷平衡、沉没成本、现金流、递延、试算平衡、计提减值、公允价值、合并报表 |
| 法律/法考 | 请求权基础、举证责任、不当得利、无因管理、诉讼时效 |
| 编程/技术 | 复杂度、重构、内存泄漏、递归、边界条件、API契约 |
| 医学/护理 | 鉴别诊断、金标准、预后、并发症、给药途径 |

**Rule:** Never use generic "只要努力就能成功" platitudes. Every wisdom sentence must use at least one domain-specific term in a clever/reflective way.

### 4. Create Cron Job

Use the `cronjob` tool:

```
action="create"
name="<ExamName>备考倒计时"
schedule="0 <hour> * * *"    # e.g. "0 9 * * *" for daily 9am
deliver="<platform>"          # e.g. "weixin" for WeChat home channel
repeat="forever"
```

**IMPORTANT:** Check `cron.wrap_response` in config. Set to `false` so the delivery content is pure (no "--- Hermes ---" headers/footers) — especially critical for WeChat/Telegram where you want clean formatting.

```bash
hermes config set cron.wrap_response false
```

### 5. Write Self-Contained Cron Prompt

The prompt must be fully self-contained — cron jobs run with no memory and no user interaction. Structure the prompt:

See `templates/countdown-briefing-example.md` for a real output example (中级会计, 89天/备考筑基期).

```
You are a {exam_role}. Generate a daily countdown briefing.

# Exam Info
- Exam: {name}
- Exam date: {exam_date}

# Calculation
1. Use `date` command to get today
2. Calculate days to exam date
3. Determine phase based on threshold
4. Apply corresponding tone

# Output Format (exact, no preamble/suffix)
📚 {name} 倒计时
——————
⏰ 距考试：{X} 天 【{阶段标签}】
📅 {YYYY-MM-DD}

💡 今日{domain}心法：
{domain joke, ≤50 chars, must contain domain jargon}

🔥 倾力助攻：
{phase-matched encouragement, ≤60 chars, must contain domain jargon}

# Constraints
- Total ≤ {char_limit} characters
- Domain jargon required in every sentence
- No generic motivational platitudes
- Final response = pure content, no commentary
```

### 6. Verify

1. Check `hermes cron list` confirms job is created
2. Optionally trigger a test run (adjust schedule temporarily if needed)
3. Confirm `cron.wrap_response` is `false` in config
4. Verify the prompt does NOT hardcode a delivery time that contradicts the cron schedule

### 7. Troubleshoot Delivery Failures

If the cron job generates content (last_status=ok) but delivery fails:

1. **Check last_delivery_error** via `cronjob(action='list')` — this tells you the platform-level error
2. **Check gateway logs** — look at `~/.hermes/profiles/<name>/logs/gateway.log` for the specific platform error pattern (e.g., "rate limited", "disconnected", "timeout")
3. **First: rule out WeChat 24-hour session timeout** — WeChat iLink connections expire ~24h after the user's last interaction with the bot. If `last_delivery_error` says "rate limited" AND the user hasn't messaged Hermes in 24h+, the "rate limited" error is a symptom of a stale session, NOT a congestion issue. Fix: user must re-engage (send a message to Hermes) to refresh the session.
4. **Test platform independently** — use `send_message` to send a test message now. If it works, the platform connection is currently alive; the failure was likely session-related
5. **Identify timing patterns** — if failures consistently occur at the same hour across multiple days AND the user messages the bot daily, it may be genuine congestion. Move the schedule by a few hours to test
6. **Move the schedule** — change the cron delivery time using `cronjob(action='update', schedule='0 <new_hour> * * *')`
7. **Update the prompt too** — the prompt text likely mentions the old delivery time. Patch it with `cronjob(action='update', prompt='<updated text>')` so the generated briefing references the correct time
8. **Restart the gateway** — if logs show stale connection warnings or "Server disconnected" errors, restart the gateway from a terminal OUTSIDE the gateway session (see Pitfalls)

### 8. WeChat-Specific: When to Abandon Cron Delivery

WeChat's iLink protocol has a fundamental limitation: **the bot can only push messages to the user within ~24 hours of the user's last message to the bot**. After 24h of user inactivity, the session expires and delivery fails (typically showing "rate limited" in the error log, but the root cause is session expiry, not congestion). See `references/wechat-24h-session-timeout.md` for full forensics.

**Decision matrix for WeChat cron delivery:**

| User messages bot daily? | Cron delivery likely reliable? | Recommendation |
|---|---|---|
| Yes | Yes, after initial send test | Proceed but add a monitoring check after 3 days |
| No / irregularly | **No** — delivery will fail after 24h gap | Do NOT create the cron job; instead offer on-demand generation |
| Unknown / new user | Best-effort with clear warning | Warn user: "This cron delivers to WeChat, which requires you to message me at least once daily for delivery to work" |

**Fallback for unreliable delivery:** Instead of a cron job, suggest the user just ask on demand: "帮我算一下还剩多少天" / "给我今天的倒计时简报" — the agent can generate it instantly in the conversation.

## Pitfalls
- **Cron delivery wrapping:** By default, cron deliveries wrap content in "cronjob response" header + "--- Hermes --- to stop..." footer. MUST set `cron.wrap_response: false` before creating the job, or the formatted briefing will look ugly on the target platform.
- **Cron `run` is async:** cronjob(action='run') only queues the job for the next scheduler tick window. To test immediately, temporarily change schedule to 1 minute ahead, wait, then restore.
- **Cross-profile cron jobs not visible from another profile:** The `cronjob` tool only sees jobs in the CURRENT profile's job store. Default profile cron data: `~/.hermes/cron/jobs.json`. Named profiles: `~/.hermes/profiles/<name>/cron/jobs.json`. To modify another profile's cron jobs, directly edit its `jobs.json` with `cross_profile=True` on the write.
- **Cross-profile WeChat accounts:** Each Hermes profile has its own Weixin credentials (`~/.hermes/weixin/` for default, `~/.hermes/profiles/<name>/weixin/` for named profiles). The cron job's delivery uses the WeChat account configured in the profile under which the cron job was created. Verify with `grep WEIXIN_ACCOUNT_ID ~/.hermes/.env` or `~/.hermes/profiles/<name>/.env`, and check `WEIXIN_HOME_CHANNEL`.
- **Date calculation in cron prompt:** Use shell `date` command inside the prompt for dynamic calculation. Do NOT hardcode today's date.
- **Domain metaphors:** If you don't know the domain well enough, use `web_search` to gather common industry terms/inside jokes before writing the prompt.
- **Character count:** WeChat mobile renders ~20-25 Chinese chars per line. 400 total chars means ~16-20 lines max. Keep it tight.
- **Prompt hardcodes delivery time:** The cron prompt is a self-contained instruction that often says "每天早上 {hour}:00". If you update the cron schedule with `cronjob(action='update', schedule='...')`, the prompt can still reference the OLD time. Always update the prompt text to match the new schedule.
- **Gateway restart blocked from inside:** `hermes gateway restart` refuses if you're inside a gateway conversation (to prevent restart loops). To force a refresh, kill the gateway PID or run `hermes gateway start` from a separate terminal session outside the gateway.
- **WeChat 24-hour session timeout (most common culprit):** WeChat iLink sessions expire ~24h after the user's last message. Cron delivery failures showing "rate limited" are usually caused by session expiry, not network congestion. Verify by checking when the user last messaged Hermes. If >24h ago, session refresh is needed before delivery will work again.
- **Do NOT chase false "rate limited" signals:** When a WeChat cron job fails with "rate limited", always first check user activity recency. Moving the schedule to a different hour (as one might for genuine rate limiting) does not help if the root cause is session expiry. Distinguish: genuine rate limiting has no error description other than "rate limited" and happens at the same hour consistently even when user is active; session expiry produces the same error text but happens regardless of hour and clears when the user re-engages.

## Related Skills

- `daily-briefing` — daily AI/International/Finance news briefing, also uses cron + WeChat delivery. Same delivery infra, different content domain.
- `hermes-agent` — general cron job creation CLI reference.

## Reference Files

- `templates/countdown-briefing-example.md` — real output example for 中级会计考试 (89天/备考筑基期), with phase-by-phase tone samples
- `references/accounting-domain-jargon.md` — complete 会计术语映射表和造句原则
- `references/wechat-24h-session-timeout.md` — WeChat 24h session expiry forensics, distinguishing genuine rate limiting from stale sessions