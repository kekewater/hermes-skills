# OpenAI 账单/用量查询限制

## 核心结论
OpenAI的账单和用量API **不能用普通API Key（sk-proj-...）查询**。需要browser session key。

## 尝试过的端点及结果

| 端点 | HTTP方法 | Key类型 | 结果 |
|------|---------|---------|------|
| `/v1/dashboard/billing/subscription` | GET | secret key | ❌ "must be made with a session key" |
| `/v1/dashboard/billing/usage` | GET | secret key | ❌ "must be made with a session key" |
| `/v1/organization/usage` | GET | secret key | ❌ "Invalid URL" |
| `/v1/organization/credit_grants` | GET | secret key | ❌ "Invalid URL" |
| `/v1/models` | GET | secret key | ✅ 可用（验证key有效性） |

## 对比：DeepSeek
DeepSeek 有公开的 `/user/balance` 端点，直接用 API Key 即可查询余额：
```bash
curl -s -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  https://api.deepseek.com/user/balance
```
返回 `balance_infos[]` 含 `total_balance` / `granted_balance` / `topped_up_balance`。

## 可行的替代方案
1. **本地tracking** — 每次调用时手动记录消耗，适合低频使用（如每日一张图）
2. **手动查dashboard** — 登录 platform.openai.com → Usage 页面看
3. **browser session key** — 但从安全角度看，不应该保存/使用session key

## 验证key可用的方法
```bash
curl -s -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models | python3 -c "
import json, sys
data = json.load(sys.stdin)
models = [m['id'] for m in data.get('data', [])]
key_models = [m for m in models if any(k in m for k in ['gpt-4', 'gpt-image', 'dall-e'])]
print(f'可用模型: {len(key_models)}个')
for m in sorted(key_models): print(f'  - {m}')
"
```

## 本地记录脚本
`~/.hermes/scripts/monitor_usage.py` 维护一个 `~/.hermes/usage_log.json` 文件，每次生图/API调用时 append 一条记录。支持：
- `python3 monitor_usage.py report` — 生成WeChat友好报告
- `python3 monitor_usage.py status` — JSON全状态
- `python3 monitor_usage.py summary [天数]` — 指定天数汇总
