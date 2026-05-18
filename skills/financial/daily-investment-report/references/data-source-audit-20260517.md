# 数据源审计报告（2026-05-17）

## 代理环境变量根因

**问题**：AKShare 东方财富源报 ProxyError，同花顺JSON API 404，新浪 hq.sinajs Forbidden

**根因**：环境中 `http_proxy=http://127.0.0.1:8889`（Vultr SSH隧道代理）

**流量路径**：
```
AKShare请求 → 代理(127.0.0.1:8889) → Vultr VPS → 东财/新浪服务器
                                                  ↓
                                            ProxyError（东财拒绝代理IP）
```

**验证**：
- `curl --noproxy '*' 'https://push2.eastmoney.com/api/qt/...'` ✅ 正常返回
- `curl 'https://push2.eastmoney.com/api/qt/...'` ❌ 走代理不通

**修复方案**：调用 AKShare 前清掉环境变量：
```python
import os
for k in ['http_proxy','https_proxy','HTTP_PROXY','HTTPS_PROXY']:
    os.environ.pop(k, None)
```

## 各数据源实测状态

| 数据源 | 状态 | 耗时 | 备注 |
|--------|------|------|------|
| **腾讯财经(gtimg)** | ✅ | <1s | 最稳定，主力源 |
| **AKShare新浪个股** | ✅ | ~23s | 需清代理env，5516只 |
| **AKShare伦敦金XAU** | ✅ | ~3s | 4538.18 USD/oz |
| **同花顺网页(thshy)** | ✅ | ~5s | 偶尔反爬(57bytes)，重试即恢复 |
| **东方财富push API** | ⚠️ | <1s | 直连通，走代理不通 |
| **AKShare全球现货** | ⚠️ | >60s | 数据量大，超时风险 |
| **新浪hq.sinajs** | ❌ | — | Forbidden |
| **上金所SGE黄金** | ❌ | — | JSONDecodeError |
| **iFinD quantapi** | ❌ | — | 双token过期(-1302/-1301) |

## 日报自动化数据采集顺序

1. 腾讯财经（所有指数+商品）— 1次curl，最快
2. 同花顺行业板块（BeautifulSoup解析table）— 领涨行业TOP5
3. AKShare新浪个股（全市场获取后过滤排序）— 领涨个股TOP5（排除N开头）
    - 必须清代理env
    - 必须在脚本开头 import akshare
4. delegate_task web_search — 要闻+机构观点
5. GPT-Image-2 拼prompt生图

## 重试策略

- 同花顺网页反爬(57bytes)：sleep 3秒后重试，最多2次
- AKShare超时(>30s)：跳过，用已有数据
- GPT生图：VPS连OpenAI，重试1次
