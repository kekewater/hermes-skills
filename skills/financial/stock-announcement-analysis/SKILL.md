---
name: stock-announcement-analysis
description: 分析上市公司限售股解禁后的减持和权益变动公告，提取股份来源等关键信息
tags: [announcement, pdf, cninfo, a-share, extraction]
related_skills: [china-stock-data, tonghuashun]
---

# 上市公司解禁后减持分析工作流

## Related Skills

| 技能 | 用途 |
|------|------|
| **china-stock-data** | 上游数据源：通达讯实时行情、腾讯财经PE/市值/换手率、同花顺iFinD公告/研报、AKShare资金流向。**CNINFO公告搜索+PDF提取详见该技能的 `references/cninfo-pdf-extraction.md`** |
| **tonghuashun** | 港股/美股行情、同花顺股息率 |

## 触发条件
用户提供：
1. 公司列表（股票代码）
2. 限售解禁日
3. 减持公告和权益变动公告Excel文件

## 分析步骤

### 1. 获取公告列表
- 优先使用用户提供的Excel文件（已包含公告标题、日期等）
- 如未提供，通过CNINFO全文搜索API获取（见下文）

### 2. 下载公告PDF正文

**⚠️ 核心问题：巨潮PDF直链已404（2026-05起）**
- `static.cninfo.com.cn/finalpage/...` 格式的旧PDF直链已全部失效
- `disc.static.szse.cn/download/...` 格式的链接有时限，跨日过期
- Tushare Pro 返回的 `url` 字段也是上述已失效格式

**解决方法：用 Hermes browser 工具提取真实PDF链接**
详见 `china-stock-data` 技能的 `references/cninfo-pdf-extraction.md`：
1. 用browser打开公告列表页 → `get attr` 提取 `announcementId`
2. 用browser打开详情页 → 点击"公告下载"按钮获取未过期PDF

## 公告数据源选型指南

**优先结论：** 没有绝对不限流的公开API。公告元数据查询用CNINFO全文搜索API（免费，无Key）；PDF正文下载必须走browser工具。

---

### 一、官方源

#### 1. 巨潮资讯网 — 全文搜索API（推荐，元数据查询）

- **接口：** `POST http://www.cninfo.com.cn/new/fulltextSearch/full`
- **特点：** 无公开调用上限，支持按代码/关键词/日期搜索
- **⚠️ 不返回PDF直链** — 返回 `announcementId`（需配合browser工具获取PDF）
- **`hisAnnouncement/query` 接口已部分失效** (2026-05)，`stock=xxx` 参数不再返回结果

**用法：**
```bash
curl -s "http://www.cninfo.com.cn/new/fulltextSearch/full" \
  -H "User-Agent: Mozilla/5.0" \
  -d "searchkey=300058&pageNum=1&pageSize=10&sortName=pubdate&sortType=desc"
```

```python
import requests
resp = requests.post(
    'http://www.cninfo.com.cn/new/fulltextSearch/full',
    data={'searchkey': '002812', 'pageNum': 1, 'pageSize': 10,
          'sortName': 'pubdate', 'sortType': 'desc'},
    headers={'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded'},
    timeout=10)
data = resp.json()
for ann in data.get('announcements', []):
    print(ann['announcementId'], ann['announcementTitle'])
```

#### 2. 上交所/深交所官方接口
- **上交所：** 无公开REST API，仅盘后数据文件，需机构资质
- **深交所：** `https://www.szse.cn/api/report/ShowReport`，限50–100次/分钟
- **适用：** 仅合规机构，个人难用

---

### 二、第三方工具

#### 1. AKShare（免费、开源）
- **接口：** `ak.stock_zh_a_disclosure_report_cninfo()` 封装巨潮源
- **限制：** ≈50次/分钟，超限易临时IP封禁；需加 `time.sleep(1)` + 代理池
- **适用：** 中小批量、免费研究
- **PDF：** 同样不返回可下载直链

#### 2. Tushare Pro（付费，高配额）
- **接口：** `pro.anns_d(ts_code='300058.SZ', limit=500)`
- **配额：** 500次/分钟，总量不限
- **当前token状态：** ✅ 本机已配置，`anns_d` 接口已验证可用
- **注意：** 调用前必须先设置 `client.DataApi._DataApi__http_url = "http://tushare.xyz"`
- **⚠️ url字段已失效** — `url` 返回的是旧格式PDF直链 `https://static.cninfo.com.cn/finalpage/...`，当前返回404。需要用 `announcementId` 走browser工具提取PDF
- **用法：**
```python
import tushare as ts
import tushare.pro.client as client
client.DataApi._DataApi__http_url = "http://tushare.xyz"
pro = ts.pro_api('c8dbb3833192a3e47991b1975ad02d95a6567988826e519ba76b0ef5')
df = pro.anns_d(ts_code='600519.SH', limit=20)
# 字段：ann_date, ts_code, name, title, url
# ⚠️ url字段=PDF直链但已404，仅用announcementId配合browser获取PDF
```

#### 3. 东方财富公开API（免费、轻量）
- **接口：** `https://np-anotice-stock.eastmoney.com/api/security/ann`
- **限制：** ≈20次/分钟，适合单只股票，不适合全量批量

---

### 三、PDF获取方法对比

| 方法 | 元数据 | PDF正文 | 时效性 | 成本 |
|:--|:--:|:--:|:--:|:--:|
| CNINFO全文搜索API | ✅ | ❌ (返回announcementId) | 实时 | 免费 |
| Tushare Pro anns_d | ✅ | ❌ (url已404) | 实时 | 付费 |
| Hermes browser工具 | — | ✅ 真实未过期PDF | 实时 | 免费 |
| iFinD HTTP API | ✅ | ✅ (需token) | 实时 | 周配1万条 |

---

### 四、限流规避关键

1. **请求间隔：** 1–2秒/次，避免连续高频
2. **轮换UA：** 模拟不同浏览器，降低识别概率
3. **代理池：** 多IP轮换，突破单IP限制
4. **缓存复用：** 已下载PDF本地缓存，减少重复请求

---

### 3. 提取关键信息（从PDF正文）

读取PDF正文，搜索以下关键字：
- **"股份来源" / "减持股份来源" / "转让股份的来源"** → 直接获取来源字段
- **"首次公开发行前" / "首发前股份"** → IPO前股份
- **"非公开发行"** → 定增股份
- **"资本公积转增"** → 资本公积转增股本
- **"协议转让"** → 协议转让获得的股份
- **"股权激励"** → 股权激励取得的股份
- **"本次变动性质" / "权益变动性质"** → 判断是减持还是其他

### 4. 判断是否需要补充
- 若PDF正文中有独立的"股份来源"字段列 → 直接提取
- 若PDF正文无显式标注 → 标注"公告未显式标注"

### 5. 生成Excel
- 列：序号、股票代码、公司名称、限售解禁日、公告日期、公告标题、减持主体、公告类型、股份来源、减持方式、减持结果、备注、状态
- 区分"已确认"和"待补充"

## Pitfalls

1. **CNINFO `hisAnnouncement/query` 接口已部分失效** — 用全文搜索API (`/new/fulltextSearch/full`) 替代，参数更简单（`searchkey=股票代码`）
2. **PDF直链全部404** — 不要依赖 `adjunctUrl`、`finalpage` 或 `static.cninfo.com.cn` 格式的链接，一律用browser工具获取
3. **browser工具需要Chrome** — 先确认 `AGENT_BROWSER_EXECUTABLE_PATH` 和 `AGENT_BROWSER_ARGS` 已设置
4. **Hermes会话重启** — browser_tool.py打补丁后，**需要新会话才能生效**（当前会话已加载旧代码）
5. **公告下载链接有时限** — 即使通过browser获取，PDF链接也可能只在当日有效
