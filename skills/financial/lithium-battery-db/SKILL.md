---
name: lithium-battery-db
description: 锂电产业链产能数据库 — 8大环节×40家公司。电芯/正极/负极/隔膜/电解液/铜箔/铝箔/粘结剂导电剂，2025-2028年产能规划+技术路线+海外布局+供应长协。
version: 3.0.0
metadata:
  hermes:
    tags: [lithium, battery, ev, supply-chain, capacity, industry-research]
    related_skills: [china-stock-data, stock-announcement-analysis]
---

# 锂电产业链产能数据库

## Overview

覆盖 **8大环节 × 40家公司** 的产能数据库，2025-2028年产能规划。

| 环节 | 公司数 | 单位 | 2025e合计 | 2028e合计 | 增幅 |
|:---|:---:|:---:|---:|---:|---:|
| 🔋 电芯 | 8家 | GWh | 1,730 | 3,060 | +77% |
| 🧪 正极材料 | 6家 | 万吨 | 137 | 295 | +115% |
| ⚫ 负极材料 | 5家 | 万吨 | 122 | 250 | +105% |
| 📄 隔膜 | 3家 | 亿㎡ | 140 | 290 | +107% |
| 🧴 电解液 | 4家 | 万吨 | 130 | 245 | +88% |
| 🟤 铜箔 | 3家 | 万吨 | 21 | 46 | +119% |
| ⚪ 铝箔 | 3家 | 万吨 | 50 | 84 | +68% |
| 🧪 粘结剂/导电剂 | 2类(5标的) | - | - | - | - |

每家企业包含：产能规划(25e-28e) + 技术路线 + 海外基地进度 + 供应长协 + 数据来源标注。

## 数据文件位置

```
~/.hermes/skills/financial/lithium-battery-db/
├── 锂电产业链产能数据库_v3.xlsx  ← 最新整合版（推荐）
├── 锂电产业链产能数据库_v2.xlsx  ← 旧版（无总览，已废弃）
├── 锂电产业链产能数据库.xlsx      ← 旧版v1
├── data/capacity/
│   ├── cell.json          # 电芯 (8家)
│   ├── cathode.json       # 正极 (6家)
│   ├── anode.json         # 负极 (5家)
│   ├── separator.json     # 隔膜 (3家)
│   ├── electrolyte.json   # 电解液 (4家)
│   ├── copper_foil.json   # 铜箔 (3家)
│   ├── aluminum_foil.json # 铝箔 (3家)
│   └── additives.json     # 粘结剂/导电剂 (2类5标)
├── data/update_log.json   # 公告扫描 + PDF验证记录
├── scripts/
│   ├── export_excel_v3.py # ★ Excel导出(v3版) — 总览+8环节+CAGR+数据来源列
│   ├── export_excel.py    # 旧版导出(无总览)
│   ├── update_db.py       # 巨潮公告自动监测
│   ├── build_db_v1.py     # 初始版本构建
│   └── build_db_v2.py     # 修正单位+补充公司
└── references/
    └── analysis_report_20260514.md  # 行业分析报告
```

## 数据来源标注规范

每条公司数据的 `sources` 字段用于追溯数据出处。支持两种格式：

### 格式A：字符串列表（简版）

适用于年报名称或公开信息：

```json
"sources": [
  "2025年报(2026-03-28)",
  "可转债募集说明书(2025-03-20)"
]
```

### 格式B：对象列表（详版 — PDF验证推荐）

适用于通过 browser 工具从巨潮下载并验证的 PDF 公告，标注到具体页号和关键数据：

```json
"sources": [
  {
    "project": "自贡年产50亿平米锂电池隔离膜项目",
    "announcement": "恩捷股份：关于在自贡市投资建设锂电池隔离膜项目的公告",
    "announcement_id": "1225304895",
    "date": "2026-05-14",
    "investment": "40亿元",
    "capacity": "50亿㎡/年",
    "location": "四川省自贡市荣县",
    "structure": "恩捷持股67%, 产业合作方持股33%",
    "board_date": "2026-05-12",
    "source_file": "恩捷股份：关于在自贡市……公告.pdf",
    "source_pages": "第1-4页",
    "key_data_page_1": "投资总额40亿元, 年产50亿㎡",
    "key_data_page_2": "项目名称/地点/合作结构",
    "key_data_page_3": "建设规模, 投资规模",
    "key_data_page_4": "风险提示"
  }
]
```

每页的关键数据点单独记录，便于交叉验证。

## When to Use

- 用户询问锂电产能数据、产业链分析
- 需要某家公司电芯/正极/负极产能规划
- 对比不同企业的技术路线和海外布局
- 查看供应长协绑定情况（宁德-特斯拉/天赐-宁德等）

## How to Update

### 完整更新流水线

```bash
# 1. 用 browser 工具从巨潮拉取并验证公告PDF
#    （详见china-stock-data技能的references/cninfo-pdf-extraction.md）

# 2. 解析PDF，更新对应JSON的产能数据和sources字段
cd ~/.hermes/skills/financial/lithium-battery-db

# 3. 重新导出Excel（v3）
python3 scripts/export_excel_v3.py

# 4. 记录到update_log.json
```

### PDF验证工作流（已验证完整跑通）

```
browser打开CNINFO公告列表 → 点击公告链接 → 
详情页渲染 → 点击"公告下载"按钮 → 
PDF自动保存到~/Downloads/ → pymupdf解析文字
```

**前置条件：** 确保 agent-browser 能找到 Chrome（详见 china-stock-data → references/cninfo-pdf-extraction.md）。

### 代理恢复（当Vultr隧道断开时）

```bash
# 代理不可用时，先检查SSH隧道
ps aux | grep "ssh.*id_vultr.*8888"

# 如果断开，杀掉并重启
kill -9 $(pgrep -f "ssh.*id_vultr.*8888") 2>/dev/null
ssh -o StrictHostKeyChecking=no \
  -o ServerAliveInterval=30 -o ServerAliveCountMax=3 \
  -i /home/ubuntu/.ssh/id_vultr \
  -L 8888:127.0.0.1:8888 -C -N -f root@45.76.185.1

# 验证
curl -x http://127.0.0.1:8888 -s -o /dev/null -w '%{http_code}' \
  --max-time 10 https://www.google.com
```

代理正常时 Google 返回 200（约3-4s）。

## Key Companies

| 环节 | 公司 |
|:---|:---|
| **电芯** | 宁德时代(700→1000GWh) · 比亚迪(550→850) · 亿纬锂能(130→320) · 国轩高科(120→280) · 中创新航(80→200) · 蜂巢能源(60→150) · 瑞浦兰钧(50→140) · 欣旺达(40→120) |
| **正极** | 容百科技 · 华友钴业 · 德方纳米 · 当升科技 · 长远锂科 · 厦门钨业 |
| **负极** | 贝特瑞 · 璞泰来 · 杉杉股份 · 中科电气 · 尚太科技 |
| **隔膜** | 恩捷股份(80→170) · 星源材质 · 中材科技 |
| **电解液** | 天赐材料 · 新宙邦 · 江苏国泰 · 多氟多 |

## 最近公告验证（2026-05-14）

使用 browser 工具从 CNINFO 巨潮成功下载并解析 PDF 公告：

| 公司 | 公告 | 关键数据 | 验证状态 |
|:---|:---|---:|:---:|
| **恩捷股份** | 自贡锂电池隔离膜项目 | **50亿㎡ × 40亿元**，恩捷67%+合作方33% | ✅ PDF已下载→解析→更新到db |
| **亿纬锂能** | 启东/上杭投资协议 | announcementId已提取 | ✅ 公告已定位 |
| **容百科技** | 磷酸铁锂前驱体项目 | announcementId已提取 | ✅ 待解析 |
| **璞泰来** | 马来西亚基地 | announcementId已提取 | ✅ 待解析 |

## Common Pitfalls

1. **这不是SMM/GGII付费数据库** — 数据来源为各公司公开信息整理，用于快速参考。精确校验需结合SMM/GGII数据
2. **产能≠产量** — 表中为名义产能规划，实际产量受良率/开工率/市场影响
3. **技术路线在快速迭代** — 硅基负极/46系大圆柱/钠离子等新技术的实际放量进度可能延误
4. **海外产能受地缘政治影响** — 美国IRA/欧盟政策变化可能导致海外基地调整
5. **融资风险** — 部分中小企业的扩产计划依赖后续融资，经济下行时可能延迟
6. **代理隧道可能掉线** — Vultr SSH隧道长时间无操作可能被运营商断开，更新数据库前先验证 `curl -x http://127.0.0.1:8888 https://www.google.com`
7. **PDF 直链有时限** — 巨潮的 PDF 下载链接通常只在当天有效，跨天会过期。必须通过 browser 点击"公告下载"获取实时链接

## Verification Checklist

- [ ] `python3 scripts/export_excel_v3.py` — 重新导出后检查总览数据
- [ ] `data/capacity/separator.json` — 恩捷sources字段有PDF来源标注
- [ ] `data/update_log.json` — 每次验证后记录

## References

| 文件 | 内容 |
|------|------|
| `data/capacity/*.json` | 各环节JSON数据库（含sources标注） |
| `scripts/export_excel_v3.py` | Excel导出v3（总览+8环节+CAGR+数据来源列） |
| `scripts/update_db.py` | 巨潮公告自动监测+PDF验证集成 |
| `references/analysis_report_20260514.md` | 行业竞争格局分析报告 |
| china-stock-data → references/cninfo-pdf-extraction.md | CNINFO PDF提取完整工作流 |
