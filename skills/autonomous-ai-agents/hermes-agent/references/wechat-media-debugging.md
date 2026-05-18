# WeChat MEDIA File Delivery Debugging

## How MEDIA: Tags Get Delivered

When an agent response contains `MEDIA:/path/to/file`, the gateway's WeChat adapter processes it through this pipeline:

```
assistant response → adapter.send()
  → extract_media() [base.py:1750] — extracts MEDIA: paths from text
  → _deliver_media() [weixin.py:1627] — routes by file extension
    → send_document() [weixin.py:1749] — for docs/spreadsheets/etc.
      → _send_file() [weixin.py:1828] — AES-encrypted upload to iLink CDN
```

## 🟢 MEDIA Delivery Through Normal Replies WORKS

**Key finding (2026-05-15)**: MEDIA: file delivery through the normal assistant reply flow (writing `MEDIA:/path/to/real/file` in the agent's response text) IS reliable. Previous failures were caused by gateway instability (needed restart), not a fundamental code bug. Verified working file types: `.xlsx`, `.docx`, `.png`, `.jpg`.

**DO NOT use the `send_message` tool for WeChat file delivery** — it reuses the gateway's `_send_session` which can cause async conflicts when the message is sent concurrently with the gateway's own response delivery pipeline. Instead, just include `MEDIA:/real/path/to/file` in your direct reply — the gateway's `adapter.send()` method processes it natively.

## 🔧 Code Fix Applied (2026-05-16): Non-Existent File Skip

**Fix**: Added `os.path.isfile()` guard in `WeixinAdapter.send()` before attempting media delivery. Both the `media_files` loop (from `extract_media()`) and `local_files` loop (from `extract_local_files()`) now skip paths that don't exist on disk with a `logger.debug()` message instead of trying to send them.

**Changed file**: `gateway/platforms/weixin.py` line 1641-1657
**Effect**: Placeholder paths like `/path`, `<path>`, `文件路径` in agent responses are silently skipped instead of triggering ENOENT errors. The user no longer sees "send_document failed" warnings in gateway logs.

**Code before**:
```python
for media_path, is_voice in media_files:
    try:
        await _deliver_media(media_path, is_voice)
    except Exception as exc:
        logger.warning("[%s] media delivery failed for %s: %s", ...)
```

**Code after**:
```python
for media_path, is_voice in media_files:
    if not os.path.isfile(media_path):
        logger.debug("[%s] skipping non-existent media path: %s", self.name, media_path)
        continue
    try:
        await _deliver_media(media_path, is_voice)
    except Exception as exc:
        logger.warning("[%s] media delivery failed for %s: %s", ...)
```

## ✅ False Positive: MEDIA:/path Placeholder Triggers ENOENT

**Critical recurring issue (2026-05-15 through 2026-05-16)**: The `extract_media()` regex in `base.py:1750` has a `\S+` fallback that matches **any non-whitespace** after `MEDIA:`. When the agent writes `MEDIA:/path` as a PLACEHOLDER in its response (e.g., when explaining how to send files), the regex captures `/path` as a real file path to send.

**Consequence**: Every response that mentions the `MEDIA:` mechanism triggers:
```
send_document failed to=o9cq802C: [Errno 2] No such file or directory: '/path'
```

This error is **harmless** (text still delivers fine) but it creates log noise and gives the user the impression file sending is broken even when it isn't.

**Diagnosis**: Check gateway.log for errors with literal path `/path`, `<path>`, or `文件路径`:
```bash
grep "No such file or directory.*/path" ~/.hermes/logs/gateway.log
grep "No such file or directory.*path" ~/.hermes/logs/gateway.log
```

**Root cause**: Two sources:
1. Agent writes `MEDIA:/path` in explanatory text (habit from memory saying "回复写 MEDIA:/path")
2. Memory injection has literal `MEDIA:/path` as a working-example placeholder

**Fix for agent's behavior**: Never write `MEDIA:/path` literally in responses. Always use `MEDIA:/actual/file/path` when intending to send, or avoid the `MEDIA:` prefix entirely when explaining the mechanism. Update memory to say `MEDIA:/path/to/real/file` instead.

**Known occurrences**: Happens in ~90% of responses (any time the agent mentions file sending). Has been flagged by user multiple times as "好多次了" (too many times).

## ⏱️ iLink Rate Limiting (ret=-2, errmsg="rate limited")

**Error code**: `ret=-2` with `errmsg="rate limited"` — genuine iLink frequency limit.
**Distinct from stale session**: `ret=-2` with `errmsg="unknown error"` is a stale-session signal (same as errcode=-14), NOT a rate limit. See `_is_stale_session_ret()` in `weixin.py:96-104`.

**When it hits**: Multiple rapid sends in a short window. The exact window is undocumented (iLink is a private WeChat API). Observed behavior:
- ~5-10 messages in <60 seconds can trigger it
- Duration is LONG: attempts up to 2 minutes after hitting the limit still fail with -2
- Affects ALL sends to the same account, not just the specific endpoint
- Does NOT affect message receiving

**What doesn't help**:
- Creating a fresh HTTP session (`aiohttp.ClientSession`) — rate limit is per account, not per connection
- Short waits (10-30s) — observed still blocked after 2+ minutes
- Switching from `send_weixin_direct` to adapter.send() — both hit the same server-side limit

**What to do**:
1. **Stop sending immediately** when you get -2 rate limited
2. **Wait at least 5 minutes** before retrying
3. **Avoid burst patterns**: space sends with deliberate pauses (3-5s between messages is safe)
4. **The `_send_text_chunk` method has internal retry** (5 attempts with 1-4s backoff, then 3x backoff for rate limits) — but `send_weixin_direct()` does NOT handle rate limits with retry

**Caveat**: `send_weixin_direct()` (used by the `send_message` tool) has NO rate-limit retry logic. It calls `adapter.send()` or `adapter.send_document()` directly and returns the error immediately. If you need reliable delivery under rate limiting, use the gateway's normal response flow (write the message + MEDIA: directly), not `send_message`.

**No public rules**: iLink does not publish rate limit documentation. All knowledge is empirical.

## ⚡ Timeout Bug Fix (2026-05-16): aiohttp 3.13.5 Compatibility

**Error**: "Timeout context manager should be used inside a task"
**Root cause**: `aiohttp 3.13.5` added an internal runtime check in `ClientSession._request()` that raises `RuntimeError` when `timeout=ClientTimeout(...)` is passed to `session.post()/get()` outside of an asyncio task context. This happens when the gateway recovers a pending session and tries to send leftover responses.

**Fix**: Replaced ALL `session.post/get(timeout=ClientTimeout(...))` patterns with `async with asyncio.timeout(...)` wrapping the session call. Changes in 5 locations:

| Function | File | Change |
|----------|------|--------|
| `_api_post()` | weixin.py:367 | `ClientTimeout` → `asyncio.timeout` |
| `_api_get()` | weixin.py:387 | `ClientTimeout` → `asyncio.timeout` |
| `_upload_ciphertext()` | weixin.py:542 | `ClientTimeout` → `asyncio.timeout` |
| `_download_bytes()` | weixin.py:567 | `ClientTimeout` → `asyncio.timeout` |
| `_download_media_internal()` | weixin.py (searched) | `ClientTimeout` → `asyncio.timeout` |

**Verified**: `weixin.py` no longer contains any `ClientTimeout` imports or usages.

**Critical**: At `weixin.py` line 1643, media delivery errors are caught with just a `logger.warning()`:

```python
except Exception as exc:
    logger.warning("[%s] media delivery failed for %s: %s", self.name, media_path, exc)
```

This means the agent has **no way to know** if the file was actually delivered. The response appears to succeed because text delivery still happens. **Always check `gateway.log` when MEDIA delivery is uncertain.**

## Debugging Checklist

### 1. Check the file exists and is readable
```bash
ls -la /path/to/file
file /path/to/file  # verify mime type
```

### 2. Check gateway logs for the actual error
```bash
grep -i "media delivery failed\|_send_file\|upload" ~/.hermes/logs/gateway.log | tail -20
```

### 3. Common failure modes

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| No error but file not received | Silent warning swallow (see above) | Check `gateway.log` |
| "getUploadUrl returned neither..." | iLink CDN session expired | Restart gateway: `hermes gateway restart` |
| AES key mismatch (grey image box) | Confirmed fixed as of May 2026 | N/A — old issue |
| File too large | WeChat iLink has size limits | Reduce file size or split |
| "Not connected" | Gateway session lost | `hermes gateway status` then restart |
| MEDIA tag visible in text | `extract_media()` regex didn't match path | Check path format: must be absolute or `~/`-relative, extension must be in the known list |

### 4. Gateway recovery
```bash
# Check gateway status
hermes gateway status
~/.hermes/gateway_state.json

# Restart
hermes gateway restart

# Wait 10s for reconnect, then retry
```

### ❌ Avoid send_message tool for WeChat file delivery

The `send_message` tool calls `send_weixin_direct()` which reuses the gateway's live `_send_session`. When the agent is responding through the gateway **and** calling `send_message` for file delivery at the same time, async concurrent access to the same session can cause conflicts (message ordering issues, dropped messages, or silent failures).

**Preferred approach**: Simply write `MEDIA:/path/to/file` in your direct reply to the user. The gateway automatically extracts and delivers it.

**When send_message is useful**: To deliver files that are NOT part of your response — e.g., a cron job or background task where you aren't replying directly to a user message. In that case, use `send_message` but be aware of the session conflict risk.

## Code Locations

| File | Lines | Purpose |
|------|-------|---------|
| `gateway/platforms/weixin.py` | 1828-1924 | `_send_file()` — AES encrypt, CDN upload, iLink send |
| `gateway/platforms/weixin.py` | 1606-1669 | `send()` — orchestrates MEDIA + text delivery |
| `gateway/platforms/base.py` | 1750-1789 | `extract_media()` — regex parse of MEDIA: tags |
| `tools/send_message_tool.py` | 1533-1551 | `_send_weixin()` — one-shot send entry point |
| `gateway/platforms/base.py` | 2575-2590 | Legacy MEDIA extraction for TTS responses |
