# 每日投资晨报工作流

## 概述

系统在每日06:30通过cron job自动执行，采集多源数据 → 拼合内容 → GPT-Image-2生图 → 发微信。

## Keke偏好的内容结构

五板块纵向布局（从Keke提供的富文本格式归纳）：

```
📊 投资日报 | 日期

🇨🇳 A股（指数名 价格 涨跌幅）
🇭🇰 港股（指数名 价格 涨跌幅）
🇺🇸 美股（指数名 价格 涨跌幅 + 重点个股）
🏅 大宗商品（黄金/原油等）
📰 要闻速览（5条一句话新闻）

底部：免责声明 + 小墨自动生成
```

颜色规则：上涨🔴红色+↑，下跌🟢绿色+↓（中国习惯，和美股反的）。

## 数据源（已验证可用）

| 数据 | 来源 | 代码 | 说明 |
|------|------|------|------|
| A股指数 | 腾讯财经 | sh000001,sz399001,sz399006,sh000688,sh000016,sh000300 | 6大指数，直接HTTP GET |
| 港股指数 | 腾讯财经 | hkHSI,hkHSTECH | 恒生+恒生科技 |
| 美股指数 | 腾讯财经 | usDJI,usSPY,usQQQ | 道琼斯+标普ETF+纳指ETF |
| 重点个股(Apple) | 腾讯财经 | usAAPL | AAPL.OQ, 数据格式同, 涨跌幅准确 |
| 黄金(伦敦金) | AKShare | futures_foreign_hist(symbol='XAU') | USD/盎司, 日K最新close |
| 黄金(国内) | AKShare | spot_quotations_sge() | Au99.99, 元/克 (SGE实体现货) |
| 行业领涨TOP5 | 同花顺HTML | q.10jqka.com.cn/thshy/ | table tbody tr 前5行 |
| 个股领涨TOP5 | AKShare新浪 | stock_zh_a_spot() | 排除N开头新股后排序 |
| 原油 | 腾讯财经 | usUSO | USO ETF |

### 黄金价格的三种取法

1. **上海黄金交易所Au99.99**（元/克）— `ak.spot_quotations_sge()` → 取品种=Au99.99的最新现价
2. **伦敦金XAU**（USD/盎司）— `ak.futures_foreign_hist(symbol='XAU')` → 取close列的尾行
3. **COMEX黄金期货** — `ak.futures_global_spot_em()` → 找GC00Y或GC26M的现价

Keke指定用XAUCNY.IDC（伦敦金人民币/克）。没有直接API时，可用XAU USD/oz ÷ 31.1035 × USDCNY ≈ 元/克。目前找不到直接XAUCNY的稳定API，优先用Au99.99（上海金交所，元/克）作为替代。

### 行业领涨（同花顺HTML抓取）

```python
import requests
from bs4 import BeautifulSoup

r = requests.get('https://q.10jqka.com.cn/thshy/',
    headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')
for row in soup.select('table tbody tr')[:5]:
    cells = row.find_all('td')
    name = cells[1].get_text(strip=True)  # 板块名
    chg = cells[2].get_text(strip=True)   # 涨跌幅字符串
```

### 个股领涨（AKShare新浪源）

```python
import akshare as ak
df = ak.stock_zh_a_spot()  # 5516只A股
# 排除N开头新股
df = df[~df['名称'].str.startswith('N')]
df = df.sort_values('涨跌幅', ascending=False)
top5 = df[['名称', '最新价', '涨跌幅']].head(5)
```

EastMoney源的 `stock_zh_a_spot_em()` 被IP封禁，只能用新浪源。

### 个股行情（腾讯财经）

腾讯财经支持美股单个股票查询，代码格式 `usAAPL`、`usMSFT` 等。
返回字段中第3列是现价，第4列是昨收，用来算涨跌幅。
AAPL在腾讯财经中代码为 usAAPL，返回AAPL.OQ。

## 数据源限制

- **EastMoney永久封禁**（非临时限流）：IP 106.54.241.187 的所有连接被拒绝。所有依赖EastMoney的AKShare接口（stock_zh_a_spot_em、stock_board_industry_name_em、futures_global_spot_em等）均不可用。无需重试，直接使用替代方案。
- **Sina hq.sinajs.cn**：直接curl返回Forbidden。需要Referer: finance.sina.com.cn头。简单场景用AKShare封装（stock_zh_a_spot内部走新浪）。
- **腾讯财经 qt.gtimg.cn**：无需header，返回GBK编码需转UTF-8，~分隔格式。
- **同花顺 q.10jqka.com.cn**：返回完整HTML，解析table tbody tr即可。

## GPT-Image-2 生图集成

每天06:30的日报通过Vultr VPS直连OpenAI生成一张GPT-Image-2专业日报图。

### 为什么不能走本地代理

本服务器通过SSH隧道→Vultr VPS(45.76.185.1)的proxy.py v2.4.10翻墙。proxy.py处理小请求没问题，但GPT图片响应(>1MB)会断连（curl error 56）。必须SSH到VPS直接curl调用OpenAI API，然后scp拉回。

### 关键配置

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| model | gpt-image-2 | gpt-image-1.5中文有错字 |
| quality | low | $0.006/张，够用 |
| size | 1792x1024 | 横版适合文字多；1024x1024太挤 |
| n | 1 | 一次只出1张 |

### JSON构建注意

**必须用Python json.dump(ensure_ascii=False)**。Shell中echo/cat构建JSON含emoji和中文时，
编码转义问题会导致400 invalid_json。正确步骤：
```python
prompt = "含emoji📊的prompt..."
req = {'model': 'gpt-image-2', 'prompt': prompt, ...}
with open('/tmp/gpt_req.json', 'w') as f:
    json.dump(req, f, ensure_ascii=False)
```
然后scp文件到VPS，再ssh执行curl读取文件。

### 完整流程

1. **采集数据**（Python脚本，多源聚合）
2. **拼合prompt**（含具体数据的中文文本）
3. **Python构建JSON**（json.dump ensure_ascii=False）
4. **scp到VPS**（scp /tmp/gpt_req.json root@45.76.185.1:/tmp/）
5. **VPS上curl OpenAI**（直接访问api.openai.com，不走代理）
6. **VPS上解码**（Python base64.b64decode → PNG）
7. **scp拉回本地**（scp /tmp/gpt_out.png /tmp/）

### 质量说明

- **low** ($0.006)：中文文字准确，无可见错误。每日日报够用。月费约$0.16(1.1元)。
- **medium/high**：画质更好，但日报场景不需要。
- **gpt-image-1.5**：有零星错字（如"科创50"变"利创50"）。

### 故障处理

- SSH到VPS超时 → 跳过GPT图片，只发文字版
- API返回400 → 检查JSON编码（Python dump而非shell）
- VPS磁盘满 → ssh rm /tmp/gpt_* 清理

## 颜色规则

- 上涨（正数）：🔴红色 + ↑（中国习惯！跟美股红跌绿涨反）
- 下跌（负数）：🟢绿色 + ↓

## 相关文件

| 文件 | 用途 |
|------|------|
| `~/.hermes/scripts/gpt_image_gen.py` | GPT-Image-2生图封装脚本（VPS直连） |
| `~/.hermes/scripts/market_daily_report.py` | 数据采集脚本（JSON输出） |
| `templates/rich-daily-report-prompt.md` | 富文本日报prompt模板 |
