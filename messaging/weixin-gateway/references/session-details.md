# Weixin Group Messaging & Multi-Account Deep Dive

Session context: User had WeChat configured (account `55edc5574faa@im.bot`, home channel `o9cq80-N43zLpZ6iIBcfcgfRvoF0@im.wechat`) and asked about sending to specific group chats, then about configuring two accounts.

## Key Architectural Findings

### Platform Config is a Single Instance Dict

In `gateway/config.py::from_dict()`, the platforms loader iterates over `data["platforms"]` and produces:

```python
platforms[platform] = PlatformConfig.from_dict(platform_data)
```

where `platform` is a `Platform` enum member (`Platform.WEIXIN = "weixin"`). There is **one slot per platform type** — no multi-instance support for the same platform in a single gateway process.

This is confirmed by `gateway/platforms/weixin.py::WeixinAdapter.__init__()`, which reads a single `account_id` from `extra` or `WEIXIN_ACCOUNT_ID` env var. There is no "weixin2" or multi-account config path.

### Token Lock Prevents Duplicate Pollers

In `weixin.py`, `_acquire_platform_lock('weixin-bot-token', self._token, ...)` uses the Weixin token as the lock key. Two gateways using the same token would fail with "Another local Hermes gateway is already using this Weixin token."

### send_message Target Format

From the `send_message` tool schema:
- DM: `weixin:user_chat_id`
- Group: `weixin:group_chat_id`
- Home channel: `weixin` (bare platform name)

The `send_message(action='list')` output showed the format:
```
weixin:o9cq80-N43zLpZ6iIBcfcgfRvoF0@im.wechat (dm)
```

### Platform Enum Supports Dynamic Members (Plugin-Only)

```python
class Platform(Enum):
    WEIXIN = "weixin"
    
    @classmethod
    def _missing_(cls, value):
        # Creates dynamic members ONLY for known plugin adapters
        ...
```

This means you cannot simply add `weixin2` as a platform name — it would be rejected unless a plugin adapter exists for it.

## Multi-Account Approach: Hermes Profiles

The only supported way to run two WeChat accounts:

1. `hermes profile create weixin2` — creates `~/.hermes/profiles/weixin2/` with independent config, .env, sessions, skills, memory
2. `HERMES_PROFILE=weixin2 hermes gateway setup` — QR-login second account
3. Run both gateways: one with default profile, one with `--profile weixin2`

Gateway profile support is confirmed in `gateway/run.py`:
- `__init__` stores profile name
- `_active_profile_name()` calls `get_active_profile_name()` from `hermes_cli/profiles`
- Gateway logs show profile name in header: `gateway.profile.header`

## iLink Bot Group Limitation Sources

From Weixin adapter docs (website/docs/user-guide/messaging/weixin.md):
- The warning block about iLink bot identity not being able to join ordinary WeChat groups
- `group_policy` defaults to `disabled` (intentional, unlike WeCom where it defaults to `open`)
- Gateway logs a WARNING at startup if group_policy is anything other than `disabled`
- The statement "In practice, most deployments only get DMs to the iLink bot working reliably"

## Existing Configuration

From the active config.yaml:
```yaml
gateway:
  platforms:
    weixin:
      extra:
        dm_policy: open
        group_policy: disabled
```

And from the top-level section (likely stale leftover):
```yaml
weixin: {}
```

## Active Account

- Account ID: `55edc5574faa@im.bot`
- Home channel: `o9cq80-N43zLpZ6iIBcfcgfRvoF0@im.wechat`
- Only one target listed in `send_message(action='list')`: the home channel DM
