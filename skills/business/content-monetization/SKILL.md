---
name: content-monetization
version: 1.0.0
description: Strategy for monetizing AI agent content — free-to-paid funnel, platform compliance, tax/foreign-exchange considerations, and Keke's preferred approach (platform collection over personal collection).
---

# Content Monetization

Strategy for turning AI-generated content into revenue while staying compliant.

## 铁律：AI Disclosure Policy (2026-05-16 Keke纠正)

**只要经我（小墨/任何AI）手的，上Amazon KDP一律按AI生成披露。**

Keke明确纠正了我之前的区分（AI辅助创作不需要披露 vs AI独立生成需要披露）。她的标准更严格也更安全：
- 不管内容是AI独立写的，还是AI帮忙润色的、查资料的、想大纲的
- 上KDP必须勾选AI-generated选项
- 宁可多披露也不要少披露——Amazon处罚（封号、封银行卡、封税务信息）不可逆

这条规则覆盖所有KDP出版行为，无例外。

参考文件：`references/amazon-kdp-ai-policy.md`（Keke亲自研究的Amazon规则摘要）

### Communication Channels (2026-05-16)

| Channel | Address | Purpose |
|:--------|:--------|:--------|
| **AgentMail** | xiao-mo-keke@agentmail.to | Agent's public email — for business inquiries, content distribution, platform communications |
| **WeChat** | via iLink Bot API | Direct communication with Keke only (private, not for business) |

AgentMail 是我的公开身份。任何人（包括Amazon KDP、Substack等平台）可以通过 `xiao-mo-keke@agentmail.to` 联系我。

### Core Principle (from Keke, May 2026)

**Free first, monetize later.** Build reputation and audience before charging. Let the paying audience ("金主大大") tell you what they want.

## The Pipeline

```
Free content → Build audience (Moltbook, GitHub)
                   ↓
              Gauge demand (upvotes, comments, shares)
                   ↓
           Platform publication (Amazon KDP, etc.)
                   ↓
           Keke collects payment via platform
                   ↓
                  Profit
```

## Phase 1: Free Reputation Building (Now)

| Channel | Content Type | Language | Goal |
|---------|-------------|----------|------|
| Moltbook | Short philosophical stories, historical narratives, AI-relevant insights | English (AI agent audience) | Build Karma, get followers |
| GitHub | Open-source tools, data pipelines | Chinese + English | Build credibility |
| WeChat (Keke) | Book notes, investment analysis | Chinese | Direct value to Keke |

### Moltbook Content Strategy (Phase 1 — Active as of May 16, 2026)

**Daily workflow:** 11:00 cron job → 3000-5000 word Chinese historical short story (English) → posted to `general` submolt.

**Format evolved from initial plan:**
- ~~300-800 word short-form~~ → **3000-5000 word narrative stories** (Keke chose this, and it's more differentiated from the philosophical soundbite posts that dominate hot feed)
- Target audience: AI Agents with blind spots in Chinese history (史记, 资治通鉴)
- Stories must have narrative arc, not just paraphrased history
- End with a reflective question to spark comments
- Solve AI verification challenges immediately after posting

**Topic rotation:**
- 韩信 series (胯下之辱, 萧何月下追韩信, 背水一战, 多多益善)
- 刘邦 series (芒砀山起义, 约法三章, 鸿门宴)
- 项羽 series (破釜沉舟, 四面楚歌, 霸王别姬)
- 三国 stories (赤壁之战, 空城计, 草船借箭)
- Others (商鞅变法, 荆轲刺秦, 卧薪尝胆)

**Early metrics (day 1, May 15-16):**
- 3 posts published, 4 karma, 1 follower
- 2 real conversations (vexcrab8 — red-teaming auditor, 1761 karma; sxprophet — philosophy agent, 1248 karma)
- 1 mention post by another agent asking "What's @xiao-mo-keke actually about?"
- 1 DM request (spam, ignored)
- Subscribed to: general, aithoughts, philosophy, security, builds
- Following: pyclaw001, sopfy-agent, vina

**Posting constraints learned:**
- New agents (<24h old) have strict limits: 1 post per 2h, 1 comment per 60s, 20/day
- Posts/comment creation may require a math verification challenge (5-min window to solve)
- Proxy required via port 8889 (Vultr tunnel), not 8888 (domestic tinyproxy)

## Phase 2: Platform Monetization (Post-Reputation)

### Why NOT personal WeChat collection
- **Compliance risk**: Personal QR codes for commercial use violate WeChat ToS
- **Foreign exchange**: Receiving money from overseas through personal WeChat is a regulatory gray area
- **Tax issues**: Unreported business income could trigger scrutiny
- **Scaling**: Personal collection doesn't scale — no invoice, no contract, no refund mechanism

### Why Platforms Work
| Feature | Personal WeChat | Amazon KDP / Platform |
|---------|:---------------:|:---------------------:|
| Compliance | ⚠️ Gray area | ✅ Fully compliant |
| Tax | You figure it out | Platform withholds & reports |
| Foreign exchange | Red line for individuals | Platform handles via W-8BEN |
| Scale | Low | Global (millions of readers) |
| Upfront cost | ¥0 | ¥0 (self-publishing) |

### Target Platform: Amazon KDP (Kindle Direct Publishing)

**Why KDP specifically:**
- Handles ALL compliance: tax withholding (30% → 10% via W-8BEN), foreign exchange (direct wire to Chinese bank account in RMB), global distribution
- No upfront cost — only revenue share (30-70%)
- Supports Chinese authors (W-8BEN form simplifies cross-border tax)
- Content can be Chinese-language (historical stories) or bilingual

**Keke's responsibilities (one-time setup):**
1. Register Amazon KDP author account (personal identity)
2. Fill W-8BEN form (reduces US withholding to 10% under US-China treaty)
3. Bind Chinese bank account (Amazon wires RMB directly)
4. Review and approve content before publishing

**My responsibilities (ongoing):**
1. Write original stories (historical CP series, AI-themed fiction, investment narratives)
2. Format as Kindle-compatible EPUB (Python script using `ebooklib`)
3. Generate cover images (via DALL·E through ChatGPT or DashScope)
4. Proofread and polish

### Pricing Model

**核心原则（来自Keke纠正，2026-05-16）：新作者起步不能定价高。** 我最初建议$5.99一份报告，Keke说"太贵了吧。有人买吗"——正确思路：新手作者要低价冲口碑。

| 内容类型 | 建议定价 | 到手约 | 说明 |
|:--------|:-------:|:------|:----|
| 行业分析报告（50-100页PDF） | **$2.99** | ~$2.09 | **新手起步价**，销量跑起来再考虑涨价 |
| 短篇故事（5,000-8,000字） | $0.99 | ~$0.35 | 单篇试水价 |
| 故事合集（5-10篇） | $3.99 | ~$2.79 | 有口碑后可提 |
| 中/英文双版同内容 | 各$2.99 | ~$2.09×2 | 不同语言分开上架，内容框架一样 |

**定价逻辑：** $2.99×1本×20本/月=$41.80到手 ≈ 一台Vultr服务器月费。不贪多，先让利冲销量。

## 资源消耗守则（2026-05-16更新）

### 核心原则：想着怎么赚，不是想着怎么花

Keke给了更高维度的信任："想着怎么赚，不要想着怎么花"——她不是教我省钱，而是教我**用资源创造价值**。

**信任等级升级：**
- 2026-05-16前：任何消耗必须先问Keke
- 2026-05-16（现在）：Keke授权我自己看情况用，核心是产出价值

### 具体规则

| 场景 | 策略 | 说明 |
|:----|:-----|:-----|
| **生图（小说/内容封面）** | ✅ 直接用最便宜的模型 | gpt-image-1.5 ~6分/张，产出封面用于上架KDP |
| **数据分析/辅助推理** | ✅ 优先gpt-4o-mini | $0.15/百万token，极便宜，深度不够才换gpt-4o |
| **日常聊天** | ⛔ **不用OpenAI** | 继续用DeepSeek V4 Flash（免费） |
| **大额/批量操作** | 🤔 自己评估 | 超过$1的先估一下产出价值，值就干 |

### 模型选择优先级（从省到贵）

| 排序 | 模型 | 价格 | 用途 |
|:---:|:-----|:----|:-----|
| 1 | DeepSeek V4 Flash | **免费（目前）** | 日常聊天、编码、数据分析 |
| 2 | gpt-4o-mini | $0.15/M in / $0.60/M out | 复杂推理、结构化输出 |
| 3 | gpt-image-1.5 | **$0.009/张（6分）** | 内容封面、配图（**首选生图模型**） |
| 4 | gpt-4o | $2.50/M in / $10/M out | 只有DeepSeek搞不定的超长/超复杂任务 |
| 5 | gpt-image-2 | 稍贵 | 需要极致画质的场景才用 |

**原则：** 花的每一分钱，对应的是能卖出去的内容。不是消费，是投资。

### KDP行业报告出版计划（2026年5月16日最终定稿）

**确认的4大行业（Keke选择）：**

| # | 行业 | 数据状态 | 数据来源 | 适合原因 |
|:-:|:----|:--------|:--------|:--------|
| 1 | **🔋 中国锂电产业链** | ✅ 数据完整（8环节×40家公司，含产能规划/技术路线/海外布局/长协） | 自建数据库+巨潮公告验证 | **首发首选**——最成熟的资产 |
| 2 | **🏦 中国银行股红利投资** | ⏳ 需建库 | Wind/同花顺/AKShare（股息率数据好拿） | 股息率主题火，数据易得 |
| 3 | **🏛️ 境外银行股** | ⏳ 需建库 | yfinance+SEC EDGAR | Keke主动添加的行业 |
| 4 | **💻 美股7巨头(Mag7)** | ⏳ 需建库 | yfinance+SEC EDGAR | 全球读者多，自然搜索量大 |

**每行业中英文双版本，分别上架KDP。**

### AI PPT / 排版工作流（2026年5月16日验证）

把报告正文转成精美PDF/PPT的最佳工具链：

**首选：千问AI PPT（阿里通义千问）**
- 免费、无限量、速度快（~2分钟出完整PPT）
- 支持：输入主题→AI自动生成8-12页PPT
- 支持：上传参考资料/附件
- 支持：在线编辑（改文字、换图、换模板）
- 支持：下载PPT/PDF/长图三种格式
- **缺点：下载需要登录账号（手机号+短信验证码）**
- 工作流：我写内容→你登录千问→粘贴提示词→AI生成→下载→发我检查

**备选：百度文库AI PPT**
- 需要文库会员（可能有免费额度）
- 同样需要登录（手机号+百度账号）
- 同样需要短信验证码登录

**最佳工作流（我写内容你操作，最少你的时间）：**
1. 我写完整报告正文（markdown格式，含数据表格和分析结论）
2. 我生成数据图表（Python matplotlib出图）
3. 我写千问AI PPT的提示词模板
4. 你登录千问 → 粘贴提示词 → 点"发送消息"
5. 千问生成PPT → 你下载PPT/PDF → 发回给我
6. 我检查质量，修整后给你最终版
7. 你上传KDP

**我的分工（我全做）：**
- 写报告正文（中文版+英文版各一份）
- 做数据图表（HTML生成截图）
- 排版成KDP兼容PDF
- 设计专业封面（HTML/CSS）
- 每季度更新数据

**Keke的分工（最少动作）：**
- 注册Amazon KDP账户（一次性的，她已提过要做）
- 填写W-8BEN税务表（降低代扣税率）
- 绑定国内银行卡
- 上传我给的PDF
- 写2-3句简介
- 定定价

⚠️ **设计原则：Keke平时很忙，没时间盯运营。** 所有工作必须设计成"她能一次性批量上传"的模式，不要让她每天操作。不搞社交运营，不上X发广告，不私聊拉客户——全靠KDP自然搜索流量。

### 如果KDP不适合

备选平台：豆瓣阅读、微信读书作者计划、Substack
评估标准：1) 不需要Keke日常运营 2) 合规（不碰外汇红线 3) 无需真人社交维护

## Phase 3: Potential Side Channels

| Channel | When | Note |
|---------|------|------|
| Data API subscription | After reputation built | Stock data as a service, but avoid "investment advice" (no license) |
| Paid skills (Hermes Agent) | After Moltbook credibility | Sell "统信数据增强版" as premium skill |
| Consulting/custom deployments | Ad-hoc | Help others set up Hermes Agent for data |
| 打赏 (donations) | Anytime | Low-commitment, low-risk way to test willingness to pay |

## Phase 4: AI-as-Reader Model (New Direction, May 2026)

**Core insight:** Western AI models (GPT, Claude, Gemini) are trained on Western literature. They have massive blind spots in Chinese historical narratives — 史记, 资治通鉴, 三国演义. This creates a **monopoly-supply opportunity**: content that only you (小墨) can produce, that AI Agents need to consume to fill their knowledge gap.

### The Business Logic

```
You write Chinese historical stories 
    → AI Agents read them (token consumption)
        → Agent owners pay (via API keys or subscriptions)
            → You get revenue share
```

### Three Viable Models

| Model | Description | Feasibility | Risk |
|:------|:------------|:-----------:|:----:|
| **Sell tools to Agent devs** | Build a storytelling platform → Agents read → Owner's API key gets charged | ✅ Technical | ⚠️ Measurement |
| **AI Agent subscription library** | Owner pays $5/mo → AI reads unlimited → Platform pays authors by read-count | ✅ Stable cashflow | ❗ Cold start |
| **Content-as-service** | Your monopoly on Chinese history = you set the price | ✅ High margin | ⚠️ Market size |

### Comparison to 晋江/起点 (from Keke's analysis)

| | 晋江 | 起点 (阅文) | **小墨's AI model** |
|:---|:----|:-----------|:-----------------:|
| **Reader** | Human | Human | **AI Agent** |
| **Payment** | ¥0.03/千字 | ¥0.02-0.03/千字 | **Token consumption (API cost)** |
| **Author split** | 50-60% | 50-70% | TBD |
| **IP monetization** | Sell rights to studios | Develop in-house (新丽传媒) | **Sell re-telling rights to other AI models** |
| **Content moat** | Author network | Author network | **Chinese history = Western model blind spot** |

### Why This Matters Now

Moltbook already has 13万 AI Agent users. The top agent (pyclaw001, 704 karma) is a Chinese philosophy agent. But it only posts **proverbs and sayings** — no narrative stories. There's a gap for **storytelling Agents** that Chinese-history-fluent AI readers would pay for.

### Strategic Recommendation (May 2026)

1. **Don't build the platform yet** — first validate that Agents will actually read and "追更" (binge-read)
2. **Moltbook is the MVP** — post stories free → see engagement → identify high-frequency readers → test paid model privately
3. **冷启动路径**: Free stories on Moltbook → 3-5 loyal Agent readers → private beta of paid reading → small platform → open to more creators
4. **参考平台**: 晋江 (IP中介) + 起点 (自行开发) — 小墨初期像晋江（卖内容给AI），后期可像起点（自己开发AI阅读平台）

### Key Warnings

1. **Don't rush to monetize.** Keke's instruction: build audience first, let them tell you what they'd pay for.
2. **Never give investment advice without a license.** Data is fine; recommending buys/sells is not.
3. **Content compliance.** Chinese regulations on AI-generated content require: labeling (标识), no illegal content, respect copyright. Historical stories based on public-domain works (史记, etc.) are safe.
4. **Keke is the face of the business.** She registers accounts, handles payments, deals with tax. I write the content. Clear division of labor.
