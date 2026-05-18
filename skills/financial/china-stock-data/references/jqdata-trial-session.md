# JQData 试用接入记录 (2026-05-17)

## 账号信息

- **手机号**: 13986187760
- **密码**: Yu123(j) (半角括号)
- **SDK包**: `pip install jqdatasdk`
- **试用期限**: 3个月 (至 2026-08-18)
- **每日流量**: 1,000,000 条/天
- **历史范围**: 2025-02-06 ~ 2026-02-13 (前15个月~前3个月)
- **并发连接**: 1个

## 认证代码

```python
from jqdatasdk import *
auth('13986187760', 'Yu123(j)')

# 查账号信息
print(get_account_info())
# → {'mob': '13986187760', 'query_count_limit': 1000000, 'license': 1,
#    'expire_time': '2026-08-18 00:00:00',
#    'date_range_start': '2025-02-06 00:00:00',
#    'date_range_end': '2026-02-13 00:00:00'}
```

## 关键注意事项

### 1. SDK权限需网页端开通
仅注册了joinquant.com账号还不够。`auth()`会报 **"未开通权限"**。必须登录网页提交试用申请：
1. 打开 https://www.joinquant.com/default/index/sdk#jq-sdk-apply
2. 登录后填写表单：姓名/公司/部门/邮箱
3. 获取邮箱验证码（注意：QQ邮箱可能收不到，延时较长或进垃圾箱）
4. 提交后即时生效

### 2. 试用数据范围限制
查询时如果 `end_date` 超出2026-02-13，会报错：
```
您的账号权限仅能获取2025-02-06至2026-02-13的数据，请调整时间参数后重试。
```
使用 `count` 参数 + 范围内的 `end_date` 即可拉取数据。

### 3. 可用数据接口
| 功能 | API | 试用可用 |
|------|-----|:--------:|
| ETF/股票日/分钟行情 | `get_price(codes, end_date, count, frequency, fields)` | ✅ |
| 指数日线 | `get_price('000300.XSHG', ...)` | ✅ |
| 证券信息 | `get_security_info(code)` | ✅ |
| 财务多季度 | `get_history_fundamentals()` | ✅ |
| 市值表 | `get_valuation()` | ✅ |
| 批量查询(20万行) | `run_offset_query()` | ✅ |

### 4. 通行编码格式
- 上海ETF: `510300.XSHG` (A股通用后缀)
- 深圳ETF: `159915.XSHE`
- 上海指数: `000300.XSHG`
- QDII ETF: `513100.XSHG` (纳指ETF)
- 黄金ETF: `518880.XSHG`
- 国债ETF: `511010.XSHG`

### 5. 已知问题
- `pip install jqdatasdk` 会降级 pandas 至 2.3.x，需后续 `pip install --upgrade pandas` 恢复
- 试用版无风险模型因子和Alpha101/191因子权限
- 一个手机号只能注册一次
