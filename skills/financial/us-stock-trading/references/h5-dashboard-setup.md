# H5 持仓看板 — 墨渊组合实时看板

## 访问地址

`http://106.54.241.187:3000`

## 前提条件

1. 腾讯云安全组必须放行 TCP 3000 端口（来源 0.0.0.0/0）
2. Flask: `pip install flask --break-system-packages`
3. alpaca-py: `pip install alpaca-py --break-system-packages`
4. `~/.hermes/portfolio/墨渊组合.json` 存在
5. `~/.hermes/data/alpaca_config.json` 存在

## 启动/关闭

```bash
cd ~/.hermes && python3 scripts/portfolio_h5.py &      # 启动
pkill -f portfolio_h5.py                                  # 关闭
```

进程监听 `0.0.0.0:3000`，30秒自动刷新。

## 数据源

- **A股ETF**: 腾讯财经 `qt.gtimg.cn`（国内直连，无需代理）
- **美股**: Alpaca Paper Trading API（需硅谷隧道8889代理）
- **汇率**: USD/CNY 实时（open.er-api.com，缓存5分钟，国内直连）
  - 函数: `get_usd_cny()` in `portfolio_h5.py` — 自动取实时汇率，缓存5分钟避免重复请求
  - 回退: API失败时使用上次成功值（不是6.83硬编码）
  - 页面右上角金色大字实时显示 `USD/CNY X.XXXX`

## 持仓配置

A股ETF组合配置在 `~/.hermes/portfolio/墨渊组合.json`。更新后重启Flask即可。

## 每只持仓显示布局（用户确认最终版 — 2026-05-18，经3+轮迭代）

每只ETF/股票分两行显示，数据行用6列CSS grid等宽对齐：

```
[第一行] 名称 代码
[第二行] 成本 ¥X.XXX | 现价 ¥X.XXX | 市值 ¥XX,XXX | 持仓 XX股 | 盈亏金额 +XX | 盈亏比例 +X.XX%
```

### 显示规则

| 字段 | 格式 | 颜色 |
|------|------|------|
| 代码 | 紧凑小字跟在名称后 | 灰色 #666 |
| 成本 | 3位小数（A股）/ 2位小数（美股） | 灰色标签 + 浅色值 |
| 现价 | 同上 | 同上 |
| 市值 | 取整，千分位 | 同上 |
| 持仓 | 整数 | 同上 |
| 盈亏金额 | + 或 -，取整 | 红色(#e74c3c)盈 / 绿色(#27ae60)亏 |
| 盈亏比例 | +X.XX% | 同上 |

### 用户反馈历史（重要 — 设计决策依据，经3+轮迭代）

1. **不显示日涨跌幅** — 建仓后发现日涨跌幅（-0.55%）和总盈亏（+0.12%）矛盾，因为买入价低于昨收。日涨跌幅对buy-and-hold组合意义不大。去掉了。
2. **6列全在一行** — 成本、现价、市值、持仓、盈亏金额、盈亏比例放在同一个CSS grid中。用户明确拒绝盈亏单独在下面一行的布局（"为什么没在一行"）。
3. **文字在上、数字在下** — 每列标签(.lbl)在上、数字(.val)在下，不用inline格式。
4. **标签简洁** — "成本价"→"成本"，省空间。
5. **持仓作为单独列** — 中间第4列，标"持仓"标签+数字，不是小字塞在名称后。
6. **窄屏可横向滚动** — `.holding-row` 有 `overflow-x: auto`。

## 代码位置

`~/.hermes/skills/financial/us-stock-trading/scripts/portfolio_h5.py`

该文件已同步到skill目录，但实际运行的是 `~/.hermes/scripts/portfolio_h5.py` 副本。
