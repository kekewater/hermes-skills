# DeepSeek v1/usage 端点发现（2026-05-17）

## 背景

用户询问能否通过API Key查询DeepSeek历史用量（token消耗、API请求次数等），发现只有`/user/balance`端点是可用的。

## 测试结果

所有测试使用 `Authorization: Bearer sk-xxxxx` 身份认证：

| 端点 | HTTP状态码 | 响应体摘要 |
|------|-----------|-----------|
| `GET /user/balance` | ✅ 200 | 返回余额JSON |
| `GET /v1/usage` | ❌ **403** | `"Missing scopes: api.usage.read"` |
| `GET /v1/usage?start_time=X&end_time=Y` | ❌ 403 | 同上 |
| `GET /usage` | ❌ 404 | 404 Not Found |
| `GET /billing/usage` | ❌ 404 | 同上 |
| `GET /dashboard/usage` | ❌ 404 | 同上 |
| `GET /usage_records` | ❌ 404 | 同上 |
| `GET /transactions` | ❌ 404 | 同上 |

## 关键发现

`/v1/usage` 返回403而非404，说明：
1. **端点确实存在** — 404表示路径不存在，403表示API识别了这个路径但禁止访问
2. **权限不足** — `Missing scopes: api.usage.read` 说明DeepSeek在API层面预留了用量查询功能
3. **默认Key无此scope** — 普通的项目API Key没有这个scope

对比 OpenAI 的 billing 接口：
- OpenAI: `{"must be made with a session key... You made it with the following key type: secret."}`（403）
- DeepSeek: `{"Missing scopes: api.usage.read..."}`（403）

深层逻辑不同：
- OpenAI：API Key 彻底没有查账单的能力（需要浏览器session key）
- DeepSeek：API Key 有查用量的能力，但需要被授予 `api.usage.read` scope

## 可能的解决方案

1. **等待DeepSeek开放scope配置** — 可能在用户后台有"API Key权限管理"功能尚未开放
2. **使用网页dashboard** — 目前唯一能看到用量历史的地方是 platform.deepseek.com
3. **余额快照趋势法** — 本地通过定时查余额推算消耗（见主SKILL.md）

## 用户导出CSV格式

用户从 platform.deepseek.com 导出的数据格式：

### cost-2026-5.csv
```
user_id,utc_date,model,wallet_type,cost,currency
b7aa674d...,2026-05-13,deepseek-v4-flash,Paid,7.58,CNY
```

### amount-2026-5.csv
```
user_id,utc_date,model,api_key_name,api_key,type,price,amount
...,2026-05-13,deepseek-v4-flash,Tencent-Hermes,sk-1bb****7cee7,output_tokens,0.000002,456669
...,2026-05-13,...,request_count,,735
...,2026-05-13,...,input_cache_hit_tokens,0.00000002,102093056
...,2026-05-13,...,input_cache_miss_tokens,0.000001,4628712
```

### 从CSV提取的真实定价

| type | price (CNY/token) | /百万tokens |
|------|-------------------|-------------|
| output_tokens | 0.000002 | ¥2.0 |
| input_cache_miss_tokens | 0.000001 | ¥1.0 |
| input_cache_hit_tokens | 0.00000002 | ¥0.02 |

缓存命中率 ≈ 777M / (777M + 47M) = 94.3%

### 5日消费总结（2026-05-13 ~ 05-17）

- 总消费：¥69.57
- 总请求：8,122次
- Output tokens：3,531,954
- 日均：¥13.91
