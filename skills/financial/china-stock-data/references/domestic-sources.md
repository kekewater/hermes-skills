# AKShare 国内直连数据源（免代理、免Key）

以下数据源均无需翻墙（硅谷隧道），直接走国内网络即可。
调用前必须清掉代理环境变量：`os.environ.pop('HTTP_PROXY', None)` 等。

## 汇率 — 美元/人民币中间价

```python
import akshare as ak
df = ak.currency_boc_safe()
# 返回 DataFrame，含美元/欧元/日元/港币等25种货币
# 最近更新日期：最近交易日
# 列名：日期, 美元, 欧元, 日元, 港元, ...
usd = df.iloc[-1]['美元']  # 如 684.15 = 6.8415 元/美元
```

- 数据源：中国银行外汇牌价
- 频率：每日更新（交易日）
- 延迟：T+0（当日牌价，非实时波动）
- 状态：✅ 可用

## 白银 — 上海黄金交易所基准价

```python
import akshare as ak
df = ak.spot_silver_benchmark_sge()
# 返回 DataFrame：交易时间, 晚盘价, 早盘价
# 单位为 元/千克
# 示例：2026-05-13  21374.0  21454.0
```

- 数据源：上海黄金交易所
- 频率：每日更新（交易日，早晚两次定价）
- 单位：元/千克
- 状态：✅ 可用

## 黄金现货 — 上海黄金交易所

```python
df = ak.spot_quotations_sge()
# 列名：['品种', '时间', '现价', '更新时间']
# Au99.99 最新价约 560-600 元/克
price = df[df['品种']=='Au99.99'].iloc[-1]['现价']
```

- 此为上海金交所Au99.99现货连续报价，非ETF
- ⚠️ 此接口偶尔JSON解析失败（`Expecting value: line 1 column 1`），重试可恢复
- 替代方案：腾讯财经黄金ETF(159934)作为兜底

## 黄金ETF（腾讯财经，实时）

通过腾讯财经获取黄金ETF实时价：

```python
import urllib.request
resp = urllib.request.urlopen("https://qt.gtimg.cn/q=sz159934", timeout=10)
data = resp.read().decode('gbk')
# 解析 ~ 分隔字段：parts[3]=现价, parts[4]=昨收
```

- 实时更新，不含代理限制
- 但ETF价格含折溢价，不直接等于金价

## 商品期货 — 国际品种（布伦特原油等）

```python
import akshare as ak
df = ak.futures_global_spot_em()
# 返回 620+ 行，列名：['序号', '代码', '名称', '最新价', '涨跌额',
#                       '涨跌幅', '今开', '最高', '最低', '昨结',
#                       '成交量', '买盘', '卖盘', '持仓量']
# 查找布油：
oil = df[df['名称'].str.contains('布伦特原油', na=False)]
print(oil['最新价'].values[0])  # 示例: 79.3 (美元/桶)
```

- 覆盖31个品类（能源、金属、农产品等），共620+个合约
- ⚠️ **速度很慢**：首次调用需下载全部31个品类，约50-60秒
- 缓存策略：建议只在日报定时任务中调用一次，不要频繁调用
- 替代方案：腾讯财经原油ETF(USO)查询更快但只反映ETF价格

> ⚠️ **关于EastMoney源的误解澄清**
> 以前认为 EastMoney 源（所有 `_em()` 结尾的AKShare接口）从服务器IP 106.54.241.187 被"永久封禁"。实测发现根因是 **代理环境变量**：`http_proxy=http://127.0.0.1:8889` 导致连接被阻塞。
>
> 修复方法：调用前清掉代理env即可
> ```python
> os.environ.pop('HTTP_PROXY', None)
> os.environ.pop('HTTPS_PROXY', None)
> ```
>
> 用 `curl --noproxy '*'` 直接请求 EastMoney push API 返回正常数据。

## 注意事项

1. **所有国内AKShare接口必须在无代理环境下调用**
   - 环境变量 `http_proxy`/`https_proxy` 会阻塞国内网站
   - 在脚本中通过 `os.environ.pop()` 或 `--noproxy '*'` 处理
2. **`futures_global_spot_em()` 非常慢**，不要在日常查询中频繁调用
   - 实测52秒下载31个品类共620+合约
   - 适合日报定时任务批量收集，不建议即时查询
3. 以上接口都是公开免费的，无需Token/API Key
4. **加密币（比特币/以太坊）** 不在AKShare范围内
   - 通过 Finnhub 查询：`BINANCE:BTCUSDT` / `BINANCE:ETHUSDT`
   - 详见 `us-stock-data` 技能
