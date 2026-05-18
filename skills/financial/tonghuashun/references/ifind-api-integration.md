# iFinD HTTP API 集成指南

## 概述

iFinD 是同花顺的专业金融数据终端。本技能通过 HTTP API 直接调用 iFinD 数据，**无需 Windows 客户端**，Linux 上即可使用。

## API 基础信息

| 项目 | 值 |
|------|-----|
| Base URL | `https://quantapi.51ifind.com/api/v1` |
| 认证方式 | `refresh_token` → `access_token` |
| access_token 有效期 | 7天 |
| refresh_token 有效期 | 与账号到期日一致 |
| IP 绑定 | 单个 access_token 最多 20 个 IP |
| 数据量限制 | 基础数据 500万条/周，行情数据 1.5亿条/周 |

## 认证流程

```python
# 1. 用 refresh_token 获取 access_token
resp = requests.post(
    f"{BASE_URL}/get_access_token",
    headers={"Content-Type": "application/json", "refresh_token": REFRESH_TOKEN}
)
# access_token 在 resp.json()["access_token"]

# 2. 用 access_token 调用 API
resp = requests.post(
    f"{BASE_URL}/real_time_quotation",
    headers={
        "Content-Type": "application/json",
        "access_token": ACCESS_TOKEN
    },
    json={...请求参数...}
)
```

## 可用接口

| 接口 | URL 路径 | 用途 |
|------|----------|------|
| 获取 Token | `get_access_token` | 刷新 access_token |
| 实时行情 | `real_time_quotation` | 个股/指数实时行情 |
| 历史行情 | `cmd_history_quotation` | K线数据 |
| 公告查询 | `report_query` | 上交所/深交所正式公告（含PDF下载链接） |
| 经济数据库 | `edb_service` | 宏观/行业数据 |
| 智能选股 | `smart_stock_picking` | 条件选股 |
| 代码转换 | `get_thscode` | 证券代码 ↔ 同花顺代码 |

## 公告查询（report_query）详解

### 请求参数

```json
{
  "codes": "300393.SZ,600000.SH",
  "functionpara": {
    "reportType": "903"
  },
  "beginrDate": "2025-01-01",
  "endrDate": "2026-05-13",
  "outputpara": "reportDate:Y,thscode:Y,secName:Y,ctime:Y,reportTitle:Y,pdfURL:Y,seq:Y"
}
```

**参数说明：**

| 参数 | 是否必须 | 说明 |
|------|---------|------|
| `codes` | 是 | 半角逗号分隔的股票代码（`.SZ`/`.SH`后缀） |
| `functionpara.reportType` | 否 | 903=全部公告（默认）；901002004=上市公告书等 |
| `beginrDate` | 否 | 公告开始日期筛选，"YYYY-MM-DD" |
| `endrDate` | 否 | 公告截止日期筛选，"YYYY-MM-DD" |
| `outputpara` | 是 | 指定返回字段，格式如 `"reportDate:Y,reportTitle:Y,pdfURL:Y"` |
| `begincTime` / `endcTime` | 否 | 按发布时间筛选（精确到时分秒） |
| `keyWord` | 否 | 按公告标题关键词筛选（在 `functionpara` 内） |

**outputpara 可选字段：**
- `reportDate` — 公告日期
- `thscode` — 证券代码
- `secName` — 证券简称
- `ctime` — 发布时间（精确到时分秒）
- `reportTitle` — 公告标题
- `pdfURL` — 公告PDF下载链接
- `seq` — 公告唯一编号

### 响应结构

```python
result = resp.json()
# result["errorcode"] == 0 表示成功
# 数据结构：
table_dict = result["tables"][0]["table"]
# table_dict = {"reportDate": [...], "reportTitle": [...], "pdfURL": [...], ...}
# 每个 key 对应一个数组，同一下标为同一条公告
rows = []
for i in range(len(table_dict["reportDate"])):
    row = {k: table_dict[k][i] for k in table_dict}
    rows.append(row)
```

**注意：** 返回的是 `table` 字典结构（各字段为数组），**不是**数组套字典格式。必须通过 key 索引数组后按下标组装。

### PDF 阅读（提取公告正文）

`pdfURL` 字段返回 PDF 下载链接，可用 `requests.get()` 下载后通过 **PyMuPDF (fitz)** 提取文本：

```python
import fitz
resp = requests.get(pdf_url, timeout=15)
doc = fitz.open(stream=resp.content, filetype="pdf")
text = ""
for page in doc:
    text += page.get_text() + "\n"
doc.close()
```

### 常见用途：提取减持公告关键信息

从公告PDF中提取字段时，在全文搜索以下关键字：
- `股份来源` / `减持股份来源` — 股份性质（IPO前/定增/二级市场买入等）
- `减持方式` — 集中竞价/大宗交易/协议转让/询价转让
- `减持数量` / `减持价格区间` — 具体数据
- `减持原因` / `减持目的` — 背景信息
- `本次变动前持有股份` / `本次变动后持有股份` — 权益变动表
- `首发前股份` / `首次公开发行前` — IPO原始股

## 常用指标列表（实时行情）

| 指标名 | 说明 | 适用 |
|--------|------|------|
| `close` | 收盘价 | 股票 |
| `open/high/low` | 开盘/最高/最低 | 股票 |
| `change` | 涨跌额 | 股票 |
| `changeRatio` | 涨跌幅(%) | 股票 |
| `volume` | 成交量(手) | 股票 |
| `amount` | 成交额(元) | 股票 |
| `pe_ttm` | 市盈率(TTM) | 股票 |
| `turnoverRatio` | 换手率(%) | 股票 |
| `totalCapital` | 总市值(元) | 股票 |
| `amplitude` | 振幅(%) | 股票 |
| `preClose` | 前收盘价 | 股票/指数 |

## Token 配置文件

存储在 `~/.hermes/skills/financial/tonghuashun/ifind_config.json`:

```json
{
  "refresh_token": "xxx",
  "access_token": "xxx",
  "access_token_expires": "2026-05-20 16:19:21"
}
```

## 自动刷新机制

脚本中的 `ifind_api()` 函数会自动处理 Token 过期：
1. 调用 API 返回 errorcode=-1010/-1300/-1302 → Token 过期
2. 自动用 refresh_token 调用 `get_access_token` 获取新 token
3. 保存到配置文件
4. 重试原请求

## 错误码速查

| 错误码 | 含义 |
|--------|------|
| 0 | 成功 |
| -1010 | Token 已失效 |
| -1000 | 数据服务器错误 |
| -1300/-1301/-1302 | Token 无效 |
| -1303 | IP 绑定超过 20 个 |
| -4001 | 无数据 |
| -4103 | 请求过多，账号被锁 |
| -4301 | 基础数据超量(500万/周) |
| -4302 | 行情数据超量(1.5亿/周) |
