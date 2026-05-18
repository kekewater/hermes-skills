# iFinD Token 管理

## Token 生命周期

| Token | 有效期 | 获取方式 | 自动刷新 |
|-------|--------|---------|---------|
| access_token | 7天 | refresh_token 换取 | ✅ 脚本检测到 -1302 时自动触发 |
| refresh_token | 30天 | Windows iFinD 客户端手动获取 | ✅ 自动刷新时会同时保存新 refresh_token |

## 命令

```bash
# 查看当前 token 状态（过期时间）
$PY $SCRIPT ifind-status

# 手动刷新（用 refresh_token 换新 access_token）
$PY $SCRIPT ifind-refresh
```

## 主动刷新策略（推荐）

为防止「双过期」（access_token 和 refresh_token 同时失效），设置 cron 每周主动刷新：

```cron
# 每周一、四 10:00 主动刷新 iFinD token
0 10 * * 1,4 cd ~/.hermes/skills/financial/tonghuashun && .venv/bin/python3 scripts/stock_api.py ifind-refresh > /dev/null 2>&1
```

`ifind-refresh` 命令失败时静默退出（不报错），仅刷新成功时更新 `ifind_config.json`。

## 自动刷新机制（get_ifind_token()）

`stock_api.py` 的 `get_ifind_token()` 函数在检测到以下错误码时自动触发刷新：

| 错误码 | 含义 | 行为 |
|--------|------|------|
| -1010 | token 无效 | 自动刷新后重试 |
| -1300 | token 已过期 | 自动刷新后重试 |
| -1302 | access_token 已过期 | 自动刷新后重试 |
| -1301 | refresh_token 已过期 | 刷新失败 → 需要从 Windows 客户端重新获取 |

**注意**：`get_ifind_token()` 中的自动刷新逻辑会同时保存新的 `access_token` **和** `refresh_token` 到 `ifind_config.json`，避免下次 refresh_token 先过期。

## 恢复流程（双过期后）

如果 access_token 和 refresh_token 都过期（错误码 -1301），需要人工干预：

1. 在 **Windows 机器** 上打开同花顺 iFinD 客户端
2. 登录账号（账号: `htzqywb001`，密码: `htzqywb888`）
3. 使用 `ifind_token.txt` 工具获取新 token
4. 更新 `~/.hermes/data/ifind_config.json` 中的 `refresh_token` 和 `access_token`
5. 执行 `ifind-refresh` 验证新 token

## 配置存储

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "expire_time": "2026-05-24 16:13:42",
  "refresh_expire_time": "2026-06-30 11:59:17"
}
```

- `expire_time`: access_token 过期时间
- `refresh_expire_time`: refresh_token 过期时间

## 验证命令

```bash
# 测试 iFinD 行情
$PY $SCRIPT ifind-quote sh600519

# 查看返回数据是否包含 PE/市值/换手率等专业字段
# 如果 token 过期，会返回错误码并自动尝试刷新
```
