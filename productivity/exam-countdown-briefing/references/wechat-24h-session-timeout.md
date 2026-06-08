# WeChat 24-Hour Session Timeout — Forensics Guide

## The Discovery (Session 2026-06-07)

The cron job "会计中级备考倒计时" (0a151e6c21f2) ran successfully every morning at 9:00 (last_status=ok), but delivery consistently failed with:

```
delivery error: Weixin send failed: iLink sendmessage rate limited: ret=-2 errcode=None errmsg=rate limited
```

### First (Wrong) Hypothesis
Thought it was WeChat peak-hour congestion at 9:00 AM. Moved schedule to 8:00 AM. **Didn't help** — the root cause was session timeout.

### Correct Root Cause
WeChat iLink sessions expire ~24 hours after the user's **last message to the bot**. Since the user only periodically checked in, the session was always stale when the cron fired.

### Telltale Signs

| Sign | Genuine rate limiting | Session timeout |
|------|----------------------|-----------------|
| Error text | "rate limited" | "rate limited" (same!) |
| Timing | Same hour every day | Aligns with user inactivity gap |
| Test send (now) | Also fails if still congested | **Works** because user just messaged |
| Persistent? | Continues even with daily user messages | Stops when user messages daily |

## The "Rate Limited" Red Herring

The WeChat iLink bridge returns "rate limited" for **both** genuine rate limiting AND session expiry. You **cannot distinguish them from the error text alone**. The diagnostic flow:

1. Check `last_delivery_error` — if "rate limited", proceed
2. Send a test message with `send_message(target='weixin', message='test')` **now**
3. If test works → the issue was a stale session (user hadn't interacted in 24h+)
4. If test also fails → it's genuine rate limiting (try different hour or platform)

## Cross-Profile Cron Management

When managing cron jobs across profiles from within a gateway session:

- The `cronjob` tool ONLY operates on the current profile's job store
- Default profile cron data: `~/.hermes/cron/jobs.json`
- Profile 012 cron data: `~/.hermes/profiles/012/cron/jobs.json`
- To remove another profile's cron job, directly zero out its jobs array:
  ```json
  {"jobs": [], "updated_at": "2026-06-07T12:00:00+08:00"}
  ```
  Write with `cross_profile=True` to bypass the cross-profile guard.

## Gateway Log Pattern

```
WARNING: [Weixin] rate limited for o9cq80yh; backing off 3.0s before retry
... (4 retries with 3s backoff) ...
ERROR: [Weixin] send failed to=o9cq80yh: iLink sendmessage rate limited
```

After session timeout, the gateway retries 4 times with 3s backoff, then fails permanently for that delivery tick. The cron job's `last_status` remains "ok" (the prompt was generated) but `last_delivery_error` captures the failure.

## How to Confirm Session Is Alive

After the user sends ANY message to Hermes via WeChat, the session refreshes immediately. From that point, `send_message` and cron deliveries will work for ~24 hours.
