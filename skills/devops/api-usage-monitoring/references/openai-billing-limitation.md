# OpenAI账单API限制

## 核心事实

OpenAI的Dashboard/Billing API端点 **不能用普通API Key（sk-xxx）调用**，必须用browser session key。

## 验证过程

### 测试时间
2026-05-17

### 可用API Key
`sk-proj-...(已隐去)`

### 测试结果

```json
// POST /v1/dashboard/billing/subscription
// Authorization: Bearer sk-proj-...
{
  "error": "Your request to GET /v1/dashboard/billing/subscription must be made with 
            a session key (that is, it can only be made from the browser). 
            You made it with the following key type: secret."
}

// GET /v1/dashboard/billing/usage?start_date=2026-05-01&end_date=2026-05-17
// Authorization: Bearer sk-proj-...
{
  "error": "Your request to GET /v1/dashboard/billing/usage must be made with 
            a session key (that is, it can only be made from the browser). 
            You made it with the following key type: secret."
}

// GET /v1/organization/credit_grants
{
  "error": {"message": "Invalid URL (GET /v1/organization/credit_grants)", ...}
}
```

### 能做什么（✅ 可用）
- `GET /v1/models` — 验证Key有效，列出可用模型 ✅
- `POST /v1/images/generations` — 生图（gpt-image-2等）✅
- `POST /v1/chat/completions` — 聊天 ✅

### 不能做什么（❌ API Key无权限）
- 查账单/用量 ❌
- 查剩余余额 ❌
- 查订阅信息 ❌

## 对比：DeepSeek

DeepSeek有公开的余额查询端点，API Key可用：

```bash
curl -s -H "Authorization: Bearer sk-xxx" \
  https://api.deepseek.com/user/balance
```

返回：
```json
{
  "balance_infos": [{"total_balance": "132.42", ...}],
  "is_available": true
}
```

## 当前方案（已实现）

| 平台 | 查询方式 | 数据源 | 精确度 |
|------|---------|--------|--------|
| DeepSeek | API直查余额 | `/user/balance` ✅ | 实时精确 |
| OpenAI消耗 | 本地追踪 | `~/.hermes/usage_log.json` | 精确（每次生图都记账） |
| OpenAI余额 | 基准估算法 | baseline - 累计消耗 | 依赖基准准确度 |

### 余额基准法流程

1. 用户登录 `platform.openai.com` → 截图余额（如 $16.62）
2. 写入 `usage_log.json` 的 `balance_snapshot` 条目
3. `_get_openai_remaining()` 从日志读基准，减掉基准后的新消耗
4. 报告显示 "余额: $16.62" 而非 "待查"
5. 基准过期时用户重新登录一次即可覆盖

## 如果未来开放

若OpenAI开放API Key查账单，更新 `monitor_usage.py` 中的 `check_openai_billing()` 函数，替换掉当前的key-only验证。
