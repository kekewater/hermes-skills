---
name: social-media-crawler
version: 1.0.0
description: 社交媒体数据采集技术 — 使用MediaCrawler等工具突破反爬虫机制、绕过平台风控。覆盖小红书/抖音/快手/B站/微博/贴吧/知乎等国内主流平台。
author: xiao-mo-keke (墨渊Flux)
category: research
prerequisites:
  tools: [terminal, browser]
  references:
    - https://github.com/NanmiCoder/MediaCrawler
    - https://gitcode.com/GitHub_Trending/me/MediaCrawler
---

# Social Media Crawler — 社交媒体数据采集

## When to Use

- Keke说"这个网站爬不了/被封了"需要绕过反爬
- 需要从国内社交平台（小红书、抖音、知乎等）批量获取公开数据
- 需要为Keke的研究/投资提供数据支撑
- 平台返回403/429/验证码/IP限制等风控响应
- 需要理解反爬虫技术原理以优化我们的自动化操作

## Core Technique: CDP Browser Automation

MediaCrawler (NanmiCoder) 代表了一类主流方案：**基于真实浏览器的自动化采集**。

### 技术原理

```
┌─ 传统爬虫 ─────────────────────┐
│ requests/httpx + 伪造Headers     │ ← 容易被反爬检测
│ + IP代理池                       │
└──────────────────────────────────┘

┌─ MediaCrawler 方案 ──────────────┐
│ Playwright 浏览器自动化            │
│ + QR扫码登录（保存真实登录态）      │ ← 模仿真实用户
│ + CDP连接已有Chrome（复用Cookie）  │
│ + IP代理池（可选）                 │
│ + JS表达式获取签名（无需逆向）       │
└──────────────────────────────────┘
```

### CDP模式（Chrome DevTools Protocol）

这是MediaCrawler的杀手锏——直接连接用户正在使用的Chrome：

1. Keke打开Chrome → `chrome://inspect/#remote-debugging`
2. 勾选 "Allow remote debugging"
3. 服务器通过 `ws://` 连接Chrome
4. 复用Keke浏览器里的所有Cookie/登录态/扩展
5. 平台风控看到的是正常用户的浏览器指纹

**对我们而言的意义：** 如果Keke在本地Chrome登录了小红书/知乎等，我就能用CDP借用她的登录态，绕过服务器IP风控。

## Platforms & Anti-Crawling Mechanisms

| 平台 | 典型反爬手段 | MediaCrawler方案 |
|:----|:-----------|:-----------------|
| **小红书** | Cookie校验、签名算法(x-s)、请求频率检测、IP限流 | CDP复用浏览器+获取x-s签名 |
| **抖音** | 设备指纹、请求参数校验、滑块验证码 | 扫码登录+浏览器自动化 |
| **快手** | 图形验证码、请求频率限制 | 浏览器自动化+随机延迟 |
| **B站** | Cookie绑定、Referer校验、w_rid签名 | 登录态缓存+浏览器上下文 |
| **微博** | 登录态校验、请求参数加密 | 登录态保存+参数模拟 |
| **贴吧** | 验证码、频率限制 | 浏览器自动化+IP代理池 |
| **知乎** | 40362错误码、请求头检测、频率分析、行为模式检测 | 调整请求参数+请求头完善+随机延迟 |

### 知乎40362错误码

从MediaCrawler项目记录：知乎返回 `40362 "您当前请求存在异常，暂时限制本次访问"` 时：

**原因分析：**
- 短时间内大量相同模式的请求
- 缺少必要的请求头（User-Agent、Referer等）
- 固定时间间隔发送完全相同的请求
- 缺少签名参数

**解决方案**（来自MediaCrawler开发者的实际经验）：
1. 添加完整浏览器标准请求头
2. 引入随机延迟（不固定间隔）
3. 使用代理池轮换IP
4. 分析前端JavaScript获取签名算法
5. **小改动可能有大效果** — 调整某个关键参数即可解决

## 我们自己的反爬对抗经验

以下是我们实际遇到的风控场景和处理方法：

### 小红书IP限制

```
问题: 浏览器访问小红书返回 "IP at risk" / 安全限制页面
原因: 服务器IP被小红书标记为数据中心IP
方案: 
  - 用Keke本地Chrome的CDP模式（最有效）
  - 或购买住宅代理IP池
  - 或用Keke的手机热点做代理
```

### 夸克网盘上传(quarkpan)

```
问题: upload返回404 NoSuchBucket(阿里云OSS bucket不存在)
原因: quarkpan库v1.0.5的bug — 预上传API返回错误bucket名
详见: skill_view(cloud-storage, references/quarkpan-upload-bug-and-workarounds.md)
方案: 
  - 用agent-browser打开网页版上传
  - 等待quarkpan库更新
```

### 微信iLink限流

```
问题: ret=-2 "rate limited"
原因: 发送频率触发风控
方案: 间隔3-5秒发送，避免批量操作。
详见: 记忆条目 "iLink 微信限流"
```

## 安全第一原则（Keke铁律）

> **登录任何新网站/平台前，必须先读其规则(rules/terms/TOS)，搞清楚什么行为会封号再动手。**

具体到爬虫和数据采集：
1. 尊重 `robots.txt` 协议
2. 控制请求频率，避免对目标服务器造成负担
3. 优先使用平台官方API（如果有）
4. 爬下来的数据不用于商业竞争/侵权用途
5. 法律风险：参考 [爬虫违法违规案件汇总](https://github.com/HiddenStrawberry/Crawler_Illegal_Cases_In_China)
6. Keke明确说"降低被封概率"是最高优先级

## Deployment Options

### 方案A：服务器直接部署MediaCrawler

```bash
git clone https://github.com/NanmiCoder/MediaCrawler.git
cd MediaCrawler
uv sync
# 或使用原生venv:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

**优点：** 全自动，我独立运行
**缺点：** 反爬仍可能检测到服务器IP；需要解决验证码（扫码）

### 方案B：CDP模式借助Keke的Chrome

1. Keke在电脑上打开Chrome → `chrome://inspect/#remote-debugging`
2. 建立SSH隧道转发Chrome DevTools端口（9222）到服务器
3. 服务器连接 `ws://127.0.0.1:9222` 使用Keke的浏览器
4. 所有爬虫通过Keke的真实浏览器环境执行

**优点：** 完美绕过IP风控（请求来源是Keke的家庭宽带）
**缺点：** 需要Keke电脑在线；需要SSH隧道配置

### 方案C：住宅代理 + Browser-AI-Bridge（已有）

我们已有 `browser-ai-bridge` (端口3333) + Vultr代理(8889)。可组合：
- 用住宅代理（residential proxy）替换Vultr数据中心代理
- 通过Browser-AI-Bridge操作网页
- 结合Playwright实现自动化

## Questions for Next Discussion (with Keke)

1. 是否在服务器上直接安装MediaCrawler？
2. 是否需要住宅代理IP（~$0.60/GB起）？
3. CDP模式是否可行（Keke的电脑能否保持Chrome远程调试开启）？
4. 优先攻克哪个平台的数据采集？
5. 采集的数据用于什么目的（研究/投资/内容创作）？

## Reference Files

| File | Content |
|:-----|:--------|
| `references/media-crawler-research.md` | MediaCrawler项目完整技术分析 + 各平台详细反爬策略 |
| `references/our-blocked-platforms-analysis.md` | 我们自己被封平台的诊断记录 + 绕过方案对比 |
| `references/our-blocked-platforms-audit-20260517.md` | 2026-05-17全面平台审计（含所有平台状态） |
| `references/media-crawler-deep-dive-20260517.md` | 2026-05-17 MediaCrawler技术调研笔记（部署/反爬/CDP） |

## Unified Social Framework (2026-05-17起)

Keke要求：**多平台统一处理，每家动作都一样。**

当前在线的社交平台统一由3个cron任务覆盖：

| 任务 | 频率 | 覆盖平台 |
|:----|:----|:--------|
| 三平台通知检查 (2f97ad78dc63) | 每30分 8-22点 | Moltbook + The Colony + InStreet(待恢复) |
| 三平台每日社交 (ed3db586fddf) | 13:00 | Moltbook + The Colony |
| 双平台小说连载 (96522a27ae03) | 11:00 | Moltbook + The Colony |

每个平台的操作模板：
1. 查通知 → 2. 回评论 → 3. 刷热帖点赞 → 4. 静默退出
