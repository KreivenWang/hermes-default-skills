# Session 2026-06-03: Profile 012 Exam Countdown Setup

## WeChat Delivery Setup (for Profile 012)

- Active WeChat account: `2e8fa4e5b72e@im.bot`
- Home channel: `o9cq80yhcfBSmkIIWC1ulQ-o-TDg@im.wechat`
- `.env` vars: `WEIXIN_ACCOUNT_ID`, `WEIXIN_TOKEN`, `WEIXIN_HOME_CHANNEL`
- `gateway.platforms` in config.yaml: `platforms: {}` (credentials managed by gateway wizard, not inline)
- `cron.wrap_response: false` — already set in profile 012 config

## Accounting (会计中级职称) Domain Jargon Pool

| Term | Meaning | Metaphor angle |
|------|---------|----------------|
| 资产负债表 | Balance sheet | 人生/备考的底子 |
| 借贷平衡 | Debit/credit balancing | 付出和回报的关系 |
| 沉没成本 | Sunk cost | 过去已投入的别再纠结 |
| 现金流 | Cash flow | 持续输入（学习节奏） |
| 计提减值准备 | Impairment provision | 正视自己的不足 |
| 公允价值变动 | Fair value change | 对自己的估值要客观 |
| 递延所得税 | Deferred tax | 暂时的账以后要还 |
| 试算平衡表 | Trial balance | 阶段性检查对错 |
| 合并报表 | Consolidated statements | 融会贯通 |
| 少数股东权益 | Minority interest | 有些事永远算不清 |
| 借方/贷方 | Debit/Credit | 付出的/收获的 |
| 坏账准备 | Bad debt provision | 放弃一些不重要的 |
| 长期股权投资 | Long-term equity investment | 复习的长期回报 |
| 存货周转率 | Inventory turnover | 做题速度/效率 |
| 折现／贴现 | Discounting | 把未来努力折现到今天 |

## Created Cron Job

```
Job ID:     0a151e6c21f2
Name:       会计中级备考倒计时
Schedule:   0 8 * * * (daily 8:00 AM) — changed from 9:00 AM due to WeChat rate limiting
Deliver:    weixin
Repeat:     forever
Prompt:     dynamic phase-based tone (see '会计中级备考倒计时' cron prompt for full text)
```

## Phase Logic Used

| Phase | Trigger | Tone |
|-------|---------|------|
| 备考筑基期 | > 60 days | 温和坚定，厚积薄发 |
| 冲刺瓶颈期 | 30–60 days | 心理疏导，查漏补缺 |
| 强化突破期 | 14–30 days | 聚焦高频考点 |
| 考前决战期 | < 14 days | 热血果断，唤醒记忆 |

## Known Issue: WeChat Rate Limiting at 9:00 AM

- Observed consistently across 2026-06-05, 06-06, 06-07: every day at 9:00 AM, iLink sendmessage rate limited (ret=-2)
- 4 retries with 3s backoff, all fail — delivery error: "Weixin send failed: iLink sendmessage rate limited"
- Non-peak hours (11:40, 11:41) work perfectly — confirmed by `send_message` test and cron run at 11:41
- Fix: moved delivery from 9:00 → 8:00 AM to avoid congestion window
- Also updated prompt text to reference "每天早上 8:00" instead of "9:00"
- Gateway service definition was stale — `hermes gateway start` from terminal needed to refresh connection
