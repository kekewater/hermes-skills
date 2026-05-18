# aiohttp 3.13.5 ClientTimeout Compatibility Fix

## Error Signal

```
RuntimeError: Timeout context manager should be used inside a task
```

This error appears in gateway logs when calling `session.post(url, timeout=ClientTimeout(...))` or `session.get(url, timeout=ClientTimeout(...))`.

## Root Cause (aiohttp 3.13.5+)

In aiohttp 3.13.5, `ClientSession._request()` creates a `TimeoutHandle` using `self._loop` (the session's event loop). When the handle's `timer()` returns a `TimerContext`, entering the context calls `asyncio.current_task(loop=self._loop)`. If the loop reference doesn't match the running loop (or if the loop was captured at session-creation time in a different task context), `current_task()` returns `None`, and the above `RuntimeError` is raised.

This is a known aiohttp internal issue — the `ClientTimeout` object itself is fine, but the way aiohttp wraps it into a `TimerContext` that captures the loop at `TimeoutHandle` construction time can mismatch under certain async orchestration patterns (gateway restart/reconnect cycles, cross-task session sharing).

## Fix

Replace all instances of:

```python
timeout = aiohttp.ClientTimeout(total=timeout_ms / 1000)
async with session.post(url, data=body, headers=headers, timeout=timeout) as response:
    ...
```

With `asyncio.timeout()` (Python 3.11+):

```python
timeout = timeout_ms / 1000
async with asyncio.timeout(timeout):
    async with session.post(url, data=body, headers=headers) as response:
        ...
```

Same pattern applies for `session.get()` and other HTTP methods.

## Affected Pattern Locations

Anywhere `aiohttp.ClientTimeout` is passed as `timeout=` keyword to a session method:

- `session.post(url, timeout=ClientTimeout(...))`
- `session.get(url, timeout=ClientTimeout(...))`

## Files Modified in Hermes Gateway

`gateway/platforms/weixin.py` — 5 locations fixed:
- `_api_post()`
- `_api_get()`
- `_upload_ciphertext()`
- `_download_bytes()`
- `_download_media_internal()` (inline `session.get(url, timeout=ClientTimeout(total=30))`)

## Verification

After applying the fix:

1. Restart the gateway
2. Send a test message to the affected platform (WeChat in this case)
3. Check gateway logs for the absence of the `Timeout context manager` error
4. Verify the message is received end-to-end

## Pitfalls

- `asyncio.timeout()` was added in Python 3.11. If the codebase needs to support Python < 3.11, use `asyncio.wait_for()` instead — but note that `wait_for` wraps a single coroutine, not an `async with` block.
- The `ClientTimeout` object can still be used in aiohttp if constructed inline within the same async task context. The fix applies only when the error manifests.
- If the session was created with `trust_env=True` and the environment has proxy variables, those can still cause connection failures unrelated to this timeout issue.
