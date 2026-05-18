# 公告深度分析：减持/权益变动关键要素提取

## 场景

用户提供一份包含多只股票减持公告/权益变动公告标题列表的Excel，要求分析解禁日后减持情况并提取关键要素（股份来源、减持主体、减持方式、数量等）。

## 关键约束

### iFinD 每周数据量配额

| 错误码 | 含义 | 配额 |
|--------|------|------|
| -4301 | 基础数据超500万条/周 | 500万 |
| -4302 | 行情数据超1.5亿条/周 | 1.5亿 |
| -4317 | 数据量超1万条/周 | **1万** ← 最容易触达 |
| -4318 | 本月使用量超限 | 月配额 |

- **触发后**：所有 `report_query` 调用返回空，无法下载新PDF
- **恢复**：下周初自动重置，或联系同花顺销售提升配额
- **策略**：非必要不重复调用 iFinD API，充分利用已下载的 PDF 缓存

### 限售解禁日获取

在无法查看用户图片时，可使用以下替代数据源：

```python
import akshare as ak
# 新浪财经限售解禁队列（可用，无需EastMoney连接）
df = ak.stock_restricted_release_queue_sina(symbol="300393")
# 东方财富限售股解禁详情（需EM连接，可能被限流）
df = ak.stock_restricted_release_detail_em(start_date="20240101", end_date="20260513")
```

## 工作流

### 1. 理解数据来源

用户通常会提供两种类型的Excel：
- **减持公告**（`减持公告-公司公告*.xlsx`）：列包括 `公告日期, 证券代码, 公告标题, 主题, 发布日期`
- **权益变动**（`权益变动-公司公告*.xlsx`）：同上结构

**注意：** 这些 Excel 可能包含长达数年的历史数据（2011 年起），关注焦点是 **解禁日后**的发生事件。

### 2. 提取原始数据

```python
# 读取 xlsx（无需 openpyxl/pandas，用 zipfile + xml.etree.ElementTree）
import zipfile, xml.etree.ElementTree as ET

def read_xlsx(path):
    data = []
    with zipfile.ZipFile(path) as z:
        ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        # 读取 shared strings
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            tree = ET.parse(z.open('xl/sharedStrings.xml'))
            for si in tree.getroot().findall('.//s:si', ns):
                t = si.find('s:t', ns)
                strings.append(t.text if t is not None else '')
        # 读取第一个 sheet
        sheets = [f for f in z.namelist() if f.startswith('xl/worksheets/sheet')]
        tree = ET.parse(z.open(sheets[0]))
        for row in tree.getroot().findall('.//s:row', ns):
            vals = []
            for cell in row.findall('s:c', ns):
                v = cell.find('s:v', ns)
                t = cell.get('t', '')
                if v is not None and v.text:
                    if t == 's':
                        idx = int(v.text)
                        vals.append(strings[idx] if idx < len(strings) else '')
                    else:
                        vals.append(v.text)
                else:
                    vals.append('')
            if any(v for v in vals):
                data.append(vals)
    return data
```

### 3. 从标题提取初步信息

公告标题中包含丰富信息，可解析出：

| 信息 | 关键词 |
|------|--------|
| 减持主体 | `控股股东`、`实际控制人`、`持股5%以上股东`、`董事`、`高管`、`监事`、`特定股东` |
| 减持类型 | `预披露`、`实施完毕/完成`、`提前终止`、`触及1%/5%`、`期限届满`、`数量过半`、`时间过半` |
| 股份来源（部分） | `协议转让`、`可转换公司债券`、`询价转让`、`司法划转` |
| 涉及权益变动 | `权益变动`、`简式权益`、`触及5%整数倍`、`持股比例降至5%以下` |

### 4. 通过 iFinD API 获取公告PDF正文

标题信息有限，**核心要素（如股份来源）只能在PDF正文中找到**。

```python
BASE = 'https://quantapi.51ifind.com/api/v1'
headers = {'access_token': ACCESS_TOKEN, 'Content-Type': 'application/json'}

params = {
    "codes": "300393.SZ",             # 股票代码
    "beginrDate": "2025-01-01",       # 开始日期
    "endrDate": "2026-05-13",         # 截止日期
    "outputpara": "reportDate:Y,thscode:Y,secName:Y,ctime:Y,reportTitle:Y,pdfURL:Y,seq:Y"
}
resp = requests.post(f'{BASE}/report_query', json=params, headers=headers)
result = resp.json()

# 解析 response（注意：是字典套数组结构，不是列表套字典）
table_dict = result['tables'][0]['table']
rows = [{k: table_dict[k][i] for k in table_dict} for i in range(len(table_dict['reportDate']))]
```

### 5. 下载并阅读PDF正文（iFinD）

```python
import fitz  # PyMuPDF

OUT_DIR = '/home/ubuntu/announcements_pdf'
os.makedirs(OUT_DIR, exist_ok=True)

def read_pdf_text(pdf_url, save_name):
    """带缓存的PDF下载+文本提取。缓存避免重复下载，节省iFinD配额。"""
    fpath = os.path.join(OUT_DIR, save_name)
    if os.path.exists(fpath + '.txt'):
        with open(fpath + '.txt', 'r') as f:
            return f.read()                 # ✅ 命中缓存，节省API配额
    resp = requests.get(pdf_url, timeout=15)
    doc = fitz.open(stream=resp.content, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    doc.close()
    # 保存缓存
    with open(fpath + '.txt', 'w') as f:
        f.write(text)
    return text
```

**缓存策略：** PDF 文本保存到 `/home/ubuntu/announcements_pdf/{code}_{date}_{seq}.txt`。
文件名格式：`{prefix}_{reportDate}_{seq}`，可从 announcement list 中提取。
缓存命中时跳过 API 调用，直接返回已提取文本。

### 5b. iFinD 配额超限时备用方案：cninfo（巨潮资讯网）

当 iFinD 返回 `-4317`（本周数据量超1万条）时，使用巨潮资讯网作为备用数据源。

**方式一：AKShare 封装（推荐，自动处理分页）**

```python
import akshare as ak

df = ak.stock_zh_a_disclosure_report_cninfo(
    symbol='300058',           # 股票代码
    market='沪深京',            # 市场
    keyword='简式',             # 标题关键词（可选）
    start_date='20250101',
    end_date='20260513'
)
# 返回列: ['代码', '简称', '公告标题', '公告时间', '公告链接']
# 公告链接是 cninfo 详情页 URL，需从中提取 PDF 地址
```

**局限：** AKShare 版本对此接口有 rate limit。部分股票代码会返回空或报 `KeyError`（列名不匹配）。此时换用方式二。

**方式二：直接调用 cninfo 查询 API**

```python
import requests, re

headers = {'User-Agent': 'Mozilla/5.0'}

resp = requests.post(
    'http://www.cninfo.com.cn/new/hisAnnouncement/query',
    data={
        'stock': '300058',                 # 股票代码
        'pageNum': 1,
        'pageSize': 50,
        'column': 'szse_latest',
        'tabName': 'fulltext',
        'plate': 'sz',                     # sz=深交所, sh=上交所
        'seDate': '2015-01-01;2026-05-13',
        'searchkey': '简式权益',
        'isHLtitle': True,
    },
    headers=headers,
    timeout=10
)
data = resp.json()
# response 结构: {"totalAnnouncement": N, "announcements": [...]}

for ann in data.get('announcements', []):
    title = re.sub(r'<[^>]+>', '', ann.get('announcementTitle', ''))
    adj_url = ann.get('adjunctUrl', '')    # 形如: finalpage/2026-05-14/1225304374.PDF
    if adj_url:
        pdf_url = f"http://static.cninfo.com.cn/{adj_url}"
        # 后续用 fitz 提取文本（同 5a 节）
```

**PDF URL 构造规则：** `http://static.cninfo.com.cn/` + `adjunctUrl`
其中 `adjunctUrl` 格式：`finalpage/YYYY-MM-DD/{announcementId}.PDF`

**方式三：从详情页 URL 提取 announcementId**

```python
# AKShare 返回的公告链接格式:
link = 'http://www.cninfo.com.cn/new/disclosure/detail?stockCode=300649&announcementId=1217401994'

# 提取 announcementId 后用日期构造 PDF URL:
from urllib.parse import parse_qs, urlparse
params = parse_qs(urlparse(link).query)
ann_id = params['announcementId'][0]       # '1217401994'
# PDF: http://static.cninfo.com.cn/finalpage/2023-07-27/1217401994.PDF
# （日期部分 = 公告日期）
```

**cninfo 限流注意事项：**
- 请求过快会返回 HTTP 500（全空响应）
- 建议每次请求间隔 2-3 秒
- 部分股票通过 akshare 查会因内部列名不匹配报 `KeyError` — 换用方式二即可
- 先查 iFinD，配额不足再降级到 cninfo

### 6. 提取关键字段

#### 6a. 纯文本搜索

```python
KEYWORDS = {
    '股份来源': ['股份来源', '减持股份来源', '转让股份的来源', '来源为'],
    '减持方式': ['减持方式', '权益变动方式', '本次权益变动方式'],
    '减持数量': ['减持数量', '本次变动数量', '合计减持', '减持股份数量'],
    '减持价格': ['减持价格', '减持价格区间', '减持价格（元'],
    '股份性质': ['股份性质', '股份类型', '首发前股份', '非公开发行', '首次公开发行'],
    '变动前后': ['本次变动前持有股份', '本次变动后持有股份'],
    '减持原因': ['减持原因', '减持目的'],
}
```

#### 6b. PDF 表格解析（重要！）

**fitz 提取表格时，每个单元格的内容是一行独立的文本**。表格结构的"股份来源"列可能被拆成多行：

```
股份来源          ← 表头
减持              ← 列名（实际是"减持方式"的上一级表头）
方式              ← 列名
减持期间          ← 数据
减持均价          ← 数据
```

要**合并上下文**才能拼出完整含义。例如力源信息的表格：

```
股份来源
高惠谊          ← 股东名称
公司2017 年     ← 来源第1行（单元格内换行）
非公开发行       ← 来源第2行
股份及其孳息     ← 来源第3行
```

**正确提取方法：** 搜索"股份来源"后，取之后5-8行，跳过空白和表头行，串联成完整来源描述：

```python
# 表格式"股份来源"的解析模式
def extract_table_source(text):
    lines = text.split('\n')
    results = []
    i = 0
    while i < len(lines):
        if '股份来源' in lines[i]:
            # 开始收集来源数据块（接下来5-10行）
            block = []
            for j in range(i+1, min(i+10, len(lines))):
                l = lines[j].strip()
                if not l or '减持方式' in l or '减持期间' in l:
                    break  # 遇到下一列表头停止
                block.append(l)
            if block:
                results.append(' '.join(block))
            i += 10
        i += 1
    return results
```

#### 6c. 隐式来源搜索（当无"股份来源"字段时）

部分公告没有独立"股份来源"字段，需在全文中搜索来源线索：

```python
SOURCE_CLUES = ['首次公开发行前', '首发前股份', '非公开发行', 'IPO前',
                '首次公开发行并上市前', '资本公积金转增股本', '协议转让取得的']

for line in text.split('\n'):
    if any(kw in line for kw in SOURCE_CLUES):
        if any(kw in line for kw in ['股份', '股票', '持有', '来源', '减持']):
            print(f'[线索] {line.strip()[:300]}')
```

### 7. 输出结构化 Excel

```python
# 不使用 openpyxl/pandas（否则需要额外安装）
# 用 zipfile + xml 直接构造 xlsx
# 列宽建议：
cols = [5, 12, 12, 14, 14, 65, 22, 22, 55, 22, 50, 70]
# 对应：序号、股票代码、公司名称、限售解禁日、公告日期、公告标题、
#        减持/权益主体、公告类型、股份来源、减持方式、减持结果、原文备注
```

### 8. 优先级策略（节省配额）

**每次批量处理时，优先下载以下3类公告：**
1. **减持完成公告**（含'实施完毕/完成'）— 最可能包含完整股份来源+减持数量+减持价格
2. **简式权益变动报告书** — 含权益变动性质、变动前后持股、股份性质
3. **减持触及阈值公告**（含'触及1%/5%'）— 含触发时的具体数量和时间

### 9. 常见股份来源类型

从PDF正文中提取到的实际案例：

| 来源描述 | 适用场景 | 示例公司 |
|---------|---------|---------|
| **首次公开发行前持有的公司股份（含资本公积转增）** | IPO 原始股东减持 | 高伟达、道氏技术、鲍斯股份、博俊科技 |
| **非公开发行股票的股份（定增）及资本公积转增** | 定增对象减持 | 洲明科技 |
| **首发前股份** | 询价转让 | 优博讯 |
| **二级市场集中竞价买入** | 通过二级市场增持后再减持 | 力源信息 |
| **限制性股票激励授予** | 股权激励解锁后减持 | 凯伦股份 |
| **可转换公司债券转股** | 可转债转股后减持 | 蓝色光标 |

### 10. 注意事项

1. **PDF 可能不标注股份来源** — 部分公司的减持完成公告没有显式"股份来源"字段，此时需在全文搜索 `首发前`/`非公开发行`/`IPO`/`首次公开`/`资本公积` 等关键词。
2. **PDF 下载可能失败** — iFinD 的 pdfURL 有时会过期（token 绑定 IP 和时间）。失败时可尝试重新获取新 token 后重新查询。
3. **响应结构陷阱** — `report_query` 返回的是 `tables[0]["table"]` 字典结构（每个字段是数组），**不是**常见的数组套字典格式。一定要按下标组装。
4. **报告期 vs 近12个月** — 分析公告日期时注意时间范围，不要遗漏"预披露→实施完成→触及阈值"的完整事件链。
5. **批量处理策略** — 对 20 家公司×多条公告，优先下载"减持完成公告"和"简式权益变动报告书"，这两类通常包含最完整的股份来源信息。
