# 同花顺 iFinD 数据接入指南

## 两种接入方式

### 方式一：HTTP API（推荐，支持 Linux/Windows/macOS）

**不需要**安装任何客户端或 SDK，直接用 HTTP 请求访问 iFinD 数据服务器。

**系统要求**：任何能发送 HTTPS 请求的系统（Linux ✓、macOS ✓、Windows ✓）

**获取 Token：**
1. 在 Windows 上安装 iFinD 桌面客户端（https://download.10jqka.com.cn/pay/ifind/）
2. 登录你的 iFinD 账号
3. 客户端菜单中选择"工具 → refresh_token 查询/更新"
4. 复制 refresh_token

**配置文件格式**（`~/.hermes/skills/financial/tonghuashun/ifind_config.json`）：
```json
{
  "refresh_token": "xxxxx",
  "access_token": "xxxxx",
  "access_token_expires": "2026-05-20 16:19:21"
}
```

**API 基础地址**：`https://quantapi.51ifind.com/api/v1/`

**认证方式**：
- `refresh_token`：长期有效（与账号到期日一致），用于获取/刷新 access_token
- `access_token`：7天有效期，用于实际数据查询
- 请求头：`access_token: <token>` 或 `refresh_token: <token>`

**可用接口：**

| 接口 | URL 路径 | 用途 |
|------|----------|------|
| 获取 Access Token | `get_access_token` | 用 refresh_token 获取当前有效的 access_token |
| 刷新 Access Token | `update_access_token` | 获取新 access_token（使旧的全部失效） |
| 实时行情 | `real_time_quotation` | 股票/指数/基金实时数据 |
| 历史行情 | `cmd_history_quotation` | 日/周/月K线，前复权/后复权/不复权 |
| 高频序列 | `cmd_high_frequency` | 分钟级高频数据 |
| EDB 经济数据库 | `edb_service` | 宏观经济指标 |
| 智能选股 | `smart_stock_picking` | 条件选股 |
| 专题报表 | `data_pool` | 各种预定义报表 |
| 公告查询 | `report_query` | 上市公司公告（含PDF下载链接） |
| 代码转换 | `get_thscode` | 股票代码 ↔ 同花顺代码 |
| 交易日查询 | `get_trade_dates` | 交易日历 |
| 数据量统计 | `get_data_volume` | 查询本周数据使用量 |
| 组合管理 | 多个接口 | 创建/管理投资组合 |

**调用示例：**
```bash
# 实时行情
curl -X POST "https://quantapi.51ifind.com/api/v1/real_time_quotation" \
  -H "Content-Type: application/json" \
  -H "access_token: YOUR_TOKEN" \
  -d '{"codes":"600519.SH,300750.SZ","indicators":"open,high,low,close,change,changeRatio,volume,amount,pe_ttm,turnoverRatio,totalCapital"}'

# 历史K线
curl -X POST "https://quantapi.51ifind.com/api/v1/cmd_history_quotation" \
  -H "Content-Type: application/json" \
  -H "access_token: YOUR_TOKEN" \
  -d '{"codes":"600519.SH","indicators":"open,high,low,close,volume","startdate":"2026-01-01","enddate":"2026-05-13","functionpara":{"Interval":"D","CPS":"2"}}'

# 公告查询
curl -X POST "https://quantapi.51ifind.com/api/v1/report_query" \
  -H "Content-Type: application/json" \
  -H "access_token: YOUR_TOKEN" \
  -d '{"codes":"600519.SH","beginrDate":"2026-01-01","endrDate":"2026-05-13","outputpara":"reportDate:Y,thscode:Y,secName:Y,reportTitle:Y,pdfURL:Y"}'
```

**历史行情参数说明：**

| 参数 | 值 | 说明 |
|------|-----|------|
| `CPS` | `2` | 前复权（分红再投） |
| `CPS` | `1` | 不复权 |
| `CPS` | `3` | 后复权（分红再投） |
| `Interval` | `D` | 日K |
| `Interval` | `W` | 周K |
| `Interval` | `M` | 月K |
| `Interval` | `Q` | 季K |
| `Fill` | `Previous` | 非交易间隔用前一数据 |
| `Fill` | `Original` | 不处理非交易间隔 |

**常用指标（indicators）：**

| 指标 | 说明 | 适用 |
|------|------|------|
| `open` | 开盘价 | 股票/指数/基金 |
| `high` | 最高价 | 同上 |
| `low` | 最低价 | 同上 |
| `close` | 收盘价 | 同上 |
| `preClose` | 前收盘价 | 同上 |
| `change` | 涨跌额 | 同上 |
| `changeRatio` | 涨跌幅(%) | 同上 |
| `volume` | 成交量（手/股） | 股票 |
| `amount` | 成交额（元） | 同上 |
| `turnoverRatio` | 换手率(%) | 股票 |
| `pe_ttm` | 市盈率(TTM) | 股票/指数 |
| `pb` | 市净率 | 股票 |
| `totalCapital` | 总市值（元） | 股票 |
| `amplitude` | 振幅(%) | 股票 |
| `avgPrice` | 均价 | 股票 |

**错误码：**

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| `0` | 成功 | — |
| `-1010` | Token已失效 | 用 refresh_token 重新获取 |
| `-1300` | Token无效 | 同上 |
| `-1302` | Access Token过期 | 用 refresh_token 刷新 |
| `-1301` | Refresh Token过期 | 需重新从iFinD客户端获取 |
| `-4001` | 无数据 | 检查参数或日期范围 |
| `-4206` | 含错误股票代码 | 检查代码格式 |
| `-4301` | 基础数据超500万条/周 | 减少查询量 |
| `-4302` | 行情数据超1.5亿条/周 | 减少查询量 |

### 方式二：Windows 客户端 + Python SDK（传统方式）

仅限 Windows，需要安装 iFinD 桌面客户端和 Python SDK（`iFinDPy`）。

**安装步骤：**
1. 下载 iFinD 桌面客户端：https://download.10jqka.com.cn/pay/ifind/
2. 登录账号
3. 从同花顺客服或 iFinD 安装目录获取 SDK `.whl` 文件
4. `pip install iFinDPy-xxx.whl`
5. 启动 iFinD 客户端后才能调用 SDK

**注意：** SDK 不在 PyPI 上，需手动获取 `.whl` 文件。

## 常见问题

### Q: HTTP API 支持港股/美股吗？
A: 代码格式为 `00700.HK`（港股）或 `AAPL.O`（美股），前提是账号有对应市场权限。

### Q: 如何查看本周数据用量？
A: 调用 `get_data_volume` 接口。

### Q: 最大支持多少只股票同时查询？
A: 行情接口一次最多查询约 50 只股票。

### Q: Refresh Token 过期了怎么办？
A: 重新在 Windows iFinD 客户端中获取新的 refresh_token。
