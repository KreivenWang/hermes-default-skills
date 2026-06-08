---
name: exam-countdown-briefing
description: "Create cron-based daily exam countdown briefings with dynamic phase-based tone, domain-specific humor, and messaging platform delivery (WeChat/Telegram/etc.)"
version: 1.0.0
created_by: agent
tags: [cron, briefing, exam, countdown, wechat, messaging, motivation]
---

# Exam Countdown Briefing

Create a daily cron job that generates domain-specific exam countdown briefings with dynamically shifting tone based on remaining days, delivered to the user's messaging platform at a fixed time.

## When to Use

- User says "帮我设置一个XX考试倒计时简报" / "create a daily countdown for exam X"
- User provides: target exam name, exam date, preferred delivery time, delivery platform
- Any scenario needing daily motivational briefings with time-varying emotional tone

## Steps

### 1. Gather Parameters

Ask or extract:
- **Exam name** (e.g., 会计中级职称 / CFA Level 1 / 法考)
- **Exam date** (e.g., 2026-09-12)
- **Delivery time** (default: 9:00 AM)
- **Delivery platform** (default: check user's configured WeChat/Telegram/etc.)
- **Domain/industry** (for generating domain-specific wisdom — accounting, law, tech, medical, etc.)
- **Character limit** (default: 400 for WeChat mobile)

### 2. Calculate Phase Thresholds

Use shell `date` to get today's date, then compare to exam date. Define phases:

| Days remaining | Phase label | Tone |
|----------------|-------------|------|
| > 60 | 备考筑基期 | 温和坚定，厚积薄发，底层逻辑构建 |
| 30–60 | 冲刺瓶颈期 | 心理疏导，抗压，查漏补缺 |
| 14–30 | 强化突破期 | 聚焦高频考点，针对性突破 |
| < 14 | 考前决战期 | 热血果断，极简有力，唤醒肌肉记忆 |

### 3. Generate Domain-Specific Wisdom

For each domain, prepare a class of metaphors using industry jargon:

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
📅 【考试倒计时{角色}】
--------------------------------
🎯 目标考试：{name}
⏳ 距考试还剩：{X} 天 【{阶段标签}】
📅 今日日期：{YYYY-MM-DD}

💡 今日{domain_humor_name}：
{one domain-joke, ≤50 chars}

🔥 倾力助攻：
{phase-matched encouragement, ≤60 chars}

# Constraints
- Total ≤ {char_limit} characters
- Domain jargon required in each joke
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

WeChat's iLink protocol has a fundamental limitation: **the bot can only push messages to the user within ~24 hours of the user's last message to the bot**. After 24h of user inactivity, the session expires and delivery fails (typically showing "rate limited" in the error log, but the root cause is session expiry, not congestion).

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
- **Cross-profile cron jobs not visible from another profile:** The `cronjob` tool only sees jobs in the CURRENT profile's job store. To modify another profile's cron jobs, directly edit its `jobs.json` (e.g., `~/.hermes/cron/jobs.json` for default, `~/.hermes/profiles/<name>/cron/jobs.json` for named profiles) with `cross_profile=True` on the write.
- **Cross-profile WeChat accounts:** Each Hermes profile has its own Weixin credentials (`~/.hermes/profiles/<name>/weixin/`). The cron job's delivery uses the WeChat account configured in the profile under which the cron job was created. Verify with `grep WEIXIN_ACCOUNT_ID ~/.hermes/profiles/<name>/.env` and check `WEIXIN_HOME_CHANNEL`.
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
