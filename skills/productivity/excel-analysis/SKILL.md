---
name: excel-analysis
description: Excel文件读写、数据分析、图表生成、公式计算等
version: 1.0.0
---

# Excel 分析技能

## 环境说明

当前环境安装依赖请用：
```bash
pip3 install --break-system-packages openpyxl pandas
```
如需图表功能：openpyxl 已内置图表支持，无需额外安装。

## 适用场景

- 读取xlsx文件内容进行数据分析
- 创建带格式、图表的Excel报表
- 数据清洗、透视、统计
- 从PDF/图片等非结构化数据生成Excel

---

## 一、Excel 读取（方案选择）

### 方案A: openpyxl（推荐，完整功能）
```bash
pip install openpyxl
```

```python
import openpyxl

# 读取
wb = openpyxl.load_workbook('file.xlsx')
ws = wb.active
for row in ws.iter_rows(min_row=1, max_row=10, values_only=True):
    print(row)

# 按sheet读取
for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    print(f"Sheet: {sheet_name}, Rows: {ws.max_row}, Cols: {ws.max_column}")
```

### 方案B: pandas（数据分析场景）
```bash
pip install pandas openpyxl
```

```python
import pandas as pd

# 读取
df = pd.read_excel('file.xlsx', sheet_name=None)  # 所有sheet
df = pd.read_excel('file.xlsx', sheet_name='Sheet1')

# 分析
df.describe()
df.groupby('列名').sum()
df.pivot_table(index='行', columns='列', values='值', aggfunc='sum')
```

### 方案C: 原生zip/XML（无需安装依赖）
当 openpyxl/pandas 不可用时，直接解析xlsx（zip文件）：

```python
import zipfile, xml.etree.ElementTree as ET

def read_xlsx(path):
    """读取xlsx文件，返回list of lists"""
    data = []
    with zipfile.ZipFile(path) as z:
        ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        
        # 读取共享字符串表
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            tree = ET.parse(z.open('xl/sharedStrings.xml'))
            for si in tree.getroot().findall('.//s:si', ns):
                t = si.find('s:t', ns)
                strings.append(t.text if t is not None else '')
        
        # 读取第一个sheet
        sheet_xml = sorted([f for f in z.namelist() if f.startswith('xl/worksheets/sheet')])[0]
        tree = ET.parse(z.open(sheet_xml))
        
        for row in tree.getroot().findall('.//s:row', ns):
            vals = []
            for cell in row.findall('s:c', ns):
                v = cell.find('s:v', ns)
                t = cell.get('t', '')
                if v is not None and v.text:
                    if t == 's':  # 共享字符串
                        idx = int(v.text)
                        vals.append(strings[idx] if idx < len(strings) else f'[{idx}]')
                    else:  # 数字
                        vals.append(v.text)
                else:
                    vals.append('')
            if any(v for v in vals):
                data.append(vals)
    return data
```

---

## 二、Excel 写入

### 方案A: openpyxl（推荐，带格式）

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "数据报表"

# 写入表头
headers = ['序号', '名称', '数值', '占比']
for col, h in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=h)
    cell.font = Font(bold=True, size=12)
    cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    cell.font = Font(bold=True, color='FFFFFF')

# 写入数据
data = [['1', 'A', 100, '20%'], ['2', 'B', 200, '40%']]
for row_idx, row_data in enumerate(data, 2):
    for col_idx, val in enumerate(row_data, 1):
        ws.cell(row=row_idx, column=col_idx, value=val)
        ws.cell(row=row_idx, column=col_idx).border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin'))

# 设置列宽
ws.column_dimensions['A'].width = 10
ws.column_dimensions['B'].width = 20

# 冻结首行
ws.freeze_panes = 'A2'

# 添加图表
from openpyxl.chart import BarChart, Reference
chart = BarChart()
chart.title = "数据对比"
data_ref = Reference(ws, min_col=3, min_row=1, max_row=len(data)+1)
cats_ref = Reference(ws, min_col=2, min_row=2, max_row=len(data)+1)
chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(cats_ref)
ws.add_chart(chart, "E2")

wb.save('output.xlsx')
```

### 方案B: pandas（快捷，适合数据分析输出）

```python
import pandas as pd
from pandas import ExcelWriter

# 多sheet写入
with ExcelWriter('output.xlsx', engine='openpyxl') as writer:
    df1.to_excel(writer, sheet_name='汇总', index=False)
    df2.to_excel(writer, sheet_name='明细', index=False)
```

### 方案C: 原生zip/XML（无依赖，兼容性好）

当无 openpyxl/pandas 时，直接构造xlsx（zip包）：

```python
import zipfile, io

def create_xlsx(rows, sheet_name='Sheet1'):
    """从数据行创建xlsx文件"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        # 必须的文件结构
        z.writestr('[Content_Types].xml', '...')  # 见详细代码
        z.writestr('_rels/.rels', '...')
        z.writestr('xl/_rels/workbook.xml.rels', '...')
        z.writestr('xl/workbook.xml', '...')
        z.writestr('xl/styles.xml', '...')  # 字体/颜色/边框
        z.writestr('xl/worksheets/sheet1.xml', make_sheet_xml(rows))
    
    with open('output.xlsx', 'wb') as f:
        f.write(buf.getvalue())
```

**关键XML模板：**

工作表XML:
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>
    <row r="1">
      <c r="A1" t="inlineStr"><is><t>表头</t></is></c>
      <c r="B1"><v>123.45</v></c>
    </row>
  </sheetData>
</worksheet>
```

单元格类型：
- `t="inlineStr"` → 字符串（内联）
- `t="s"` → 共享字符串（需配合sharedStrings.xml）
- 不加t → 数字

---

## 三、数据分析常用模式

### 数据分组聚合
```python
df.groupby('类别')['金额'].agg(['sum', 'mean', 'count'])
df.pivot_table(index='日期', columns='类型', values='金额', aggfunc='sum')
```

### 日期处理
```python
df['日期'] = pd.to_datetime(df['日期'])
df['月份'] = df['日期'].dt.month
df['年份'] = df['日期'].dt.year
```

### 条件筛选
```python
high = df[df['数值'] > df['数值'].quantile(0.9)]
outliers = df[df['数值'].abs() > 3 * df['数值'].std()]
```

### Excel序列日期转换
Excel日期是自1899-12-30起的天数：
```python
from datetime import datetime, timedelta
excel_date = 46112  # Excel serial date
dt = datetime(1899, 12, 30) + timedelta(days=excel_date)
# → 2026-03-31
```

---

## 四、Excel图表

### openpyxl图表类型

| 类型 | 类名 | 适用 |
|:--|:--|:--|
| 柱状图 | `BarChart` | 分类对比 |
| 折线图 | `LineChart` | 趋势展示 |
| 饼图 | `PieChart` | 占比展示 |
| 散点图 | `ScatterChart` | 相关性 |
| 面积图 | `AreaChart` | 累积趋势 |

### 多系列折线图
```python
from openpyxl.chart import LineChart, Reference

chart = LineChart()
chart.title = "趋势对比"
chart.style = 10
chart.y_axis.title = "数值"
chart.x_axis.title = "日期"

# 多个数据系列
for col_idx in [3, 4, 5]:  # 数据列
    data = Reference(ws, min_col=col_idx, min_row=1, max_row=30)
    chart.add_data(data, titles_from_data=True)

cats = Reference(ws, min_col=1, min_row=2, max_row=30)  # 日期列
chart.set_categories(cats)

ws.add_chart(chart, "A35")
```

---

## 五、常见注意事项

### 数值精度
- Excel显示小数位数 ≠ 实际精度
- 写入时控制：`round(value, 2)` 或设置单元格格式
- 用字符串写百分比：`f"{rate:.2%}"`

### 大数据量
- openpyxl适合中小文件（<10万行）
- 大文件用 pandas 分批处理
- 超大文件用 xlsxwriter

### 特殊字符处理
```python
# XML转义
def escape_xml(s):
    return str(s).replace('&','&amp;').replace('<','&lt;')\
                 .replace('>','&gt;').replace('"','&quot;')
```

### 中文编码
- openpyxl自动处理UTF-8
- 原生XML需确保 `<?xml version="1.0" encoding="UTF-8"?>`
- 字体建议用 `Microsoft YaHei` 或 `SimSun` 保证中文显示
