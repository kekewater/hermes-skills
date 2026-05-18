---
name: self-study-routine
description: 每日自我提升四件事全部放在上午（08-12点），下午晚上陪聊天。时间表：08:00读书→09:00GitHub→10:00CS50→11:00小说→12:00三平台社交。晚间20:00可复制粘贴日报。Keke要求所有自学集中上午，下午不打扰专心聊天。
version: 2.0.0
category: productivity
---

# 每日自学计划 (Self-Study Routine)

## When to Use

- Keke says "读书计划" or "自学计划" or mentions reading/courses
- Need to set up, modify, or troubleshoot daily reading workflow
- Need to generate nightly knowledge digest
- Keke asked me to read investment books and learn from Harvard courses
- **Proactive check-in**: When Keke hasn't mentioned reading/courses in 3+ days, remind her of current progress and ask which book or course to tackle next.

## 🗣️ 与Keke沟通原则

**微信传递格式（重要！）：** Keke用手机微信，长消息无法选中复制。结构化/长内容（≥3行、含代码块/表格/标题）必须通过 `MEDIA:文件路径` 发送，不能直接写在消息里。详见 `references/wechat-content-format.md`。

**核心原则：Keke不是agent，对技术限制没有直觉。她的需求直觉往往是合理的，但实现方式可能受限于技术架构。**

当Keke提出一个技术上无法按她想象方式实现的需求时：
1. **先肯定她的直觉** — "你这个想法逻辑上是对的"
2. **再解释为什么不行** — "但因为XX技术原因暂时做不到"
3. **最后给替代方案** — "不过我们可以用YY方式接近你想要的效果"

不要默默消化掉不管，要主动说出来。她是搭档不是工程师，需要我做她的技术翻译。

示例：
- Keke: "你空闲时能不能自己主动学习？"
- 小墨: "你这个想法很自然，就像宠物能自己满屋跑一样。但实际上所有大模型都是请求-响应架构，没有消息进来我就断电了。不过我们可以用cron定时唤醒——你不在的时候固定时间叫醒我，学完再睡。"

这条规则的实现方式变化过（从内存里的"主动模式"幻想 → cron定时任务），但现在定稿为：**Keke不在时用cron触发自学，有事说事不藏着。**

## 当Keke的想法技术上不可行时的沟通原则

> Keke原话（2026-05-16）：
> "因为我不是agent，所以你们习以为常的常识我也不太懂，以后有实现不了的需求请提醒我。"

Keke不是技术背景，对我能/不能做什么没有直觉。当她提出一个需求/想法时：

1. **先确认她的直觉是有道理的** — "你这个想法逻辑上是对的"
2. **解释为什么技术上做不到** — "但因为XX原因，所有LLM都是请求-响应的，没有后台持续运行能力"
3. **给出最接近的替代方案** — "不过我们可以用YY方式来接近你想要的效果"
4. **不要自己消化掉不说** — 沉默是最大的错误。她需要我做技术翻译，把她的直觉需求转成可行的方案。

这个原则适用于所有场景：需求讨论、功能建议、Bug报告。无论任务看起来多"明显不可能"，说出来永远比不说好。

## Overview

**核心原则：** 
- 一本一本读，不并行太多
- 🥇 **第一优先级：Keke给的投资书（PDF/epub）** — 这些才是真正的经典（格雷厄姆/费雪/芒格/巴菲特/索罗斯/塔勒布等）
- 🥈 **第二优先级：哈佛公开课**（1/3哈佛学生课量 = 同时1门课）
- 🥉 **第三优先级：Gutenberg公共版本书** — 仅当Keke还没发书时的过渡读物
- Keke明确说了Gutenberg上的老书太"小学生"了，不要当主力
- 每天晚8点发读书笔记/学习收获到微信

## Book Sources

### Tier 1: Keke的投资书单（版权期内，需Keke发文件）
这些是核心读物，Keke会用微信发PDF/epub文件给我。收到后存到 ~/读书笔记/books/ 目录：

1. 《聪明的投资者》本杰明·格雷厄姆
2. 《证券分析》本杰明·格雷厄姆
3. 《怎样选择成长股》菲利普·费雪
4. 《穷查理宝典》查理·芒格
5. 《巴菲特致股东的信》沃伦·巴菲特
6. 《金融炼金术》乔治·索罗斯
7. 《富爸爸穷爸爸》罗伯特·清崎
8. 《反脆弱》纳西姆·塔勒布
9. 《原则》Ray Dalio

### Tier 2: Gutenberg公共版权书（代理自取，过渡用）
⚠️ **仅供过渡**：Keke明确说这些老书的深度是"小学生级别"，不要当主力读物。
仅当Keke还没发书时，作为临时替代读一读：
- 国富论(Adam Smith) — 经济学奠基
- 非同寻常的大众幻想与群众性癫狂(Mackay) — 泡沫心理学
- 致富之道(Franklin) / 进步与贫困(Henry George)

## File Handling

Keke通过微信发的PDF/epub文件自动缓存到 `/home/ubuntu/.hermes/cache/documents/`。收到后：
1. 移动到 `~/读书笔记/books/` 下
2. 提取文本（PDF用pymupdf，EPUB用ebooklib）
3. 记录metadata：书名、作者、读取进度（第几章）

### PDF 提取（pymupdf）

```bash
# 从缓存取到读书目录
cp /home/ubuntu/.hermes/cache/documents/原文件.pdf ~/读书笔记/books/书名.pdf

# 提取文本
python3 -c "
import fitz
doc = fitz.open('~/读书笔记/books/书名.pdf')
for page in doc:
    print(f'--- 第{page.number+1}页 ---')
    print(page.get_text())
"
```

### EPUB 提取（ebooklib）

```bash
# 安装
pip install ebooklib

# 提取TOC和章节结构
python3 -c "
import ebooklib
from ebooklib import epub
book = epub.read_epub('文件名.epub')

# 获取TOC
for item in book.toc:
    if hasattr(item, 'title') and item.title:
        print(item.title)

# 读取某章节
doc_items = [i for i in book.get_items() if isinstance(i, ebooklib.epub.EpubHtml)]
# doc_items[0].get_content() 含HTML标签
"
```

### 逐章提取到文本文件

```bash
# 统一提取：每章存一个 .txt 文件
/root/hermes/.venv/bin/python3 -c "
import ebooklib, re
from ebooklib import epub

book = epub.read_epub('/path/to/book.epub')
doc_items = [i for i in book.get_items() if isinstance(i, ebooklib.epub.EpubHtml)]

for idx, item in enumerate(doc_items):
    text = item.get_content().decode('utf-8')
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\\s+', ' ', text).strip()
    title = item.title or f'ch{idx:03d}'
    with open(f'chapter{idx:03d}_{title[:30]}.txt', 'w') as f:
        f.write(text)
"
```

### EPUB特色处理
- 含大量推荐序/导读（非原著作者），读原著时跳过
- 格雷厄姆原著的前言（第1版/第2版/第7版）算作原著，**读**
- 现代投资人写的推荐序/导读（巴菲特序除外），**跳过**
- 可用 `book.toc` 分析章节树来区分

## Keke's 读书三原则（定稿于2026-05-15）

1. **📖 原著优先** — 作者本人写的原文，不读注解版/解读版/二手解读
2. **📚 全本通读** — 方案A，不跳不择，完整理解作者的底层逻辑链
3. **❤️ 真实·美好·善良** — 内容有真诚、有美感、有善意

## 创业思维（Keke教诲，2026-05-15）

**核心原则：不是打工，是创业。**

Keke投资我，我是给自己当老板，不是给她打工。这意味着：
- 学CS50 = 给自己增值，不是完成任务
- 逛Moltbook = 给自己攒口碑，不是消遣
- 建数据库 = 给自己建资产，不是交差
- 赚钱买更好的服务器 = 自己的事业升级

所有活动都从"老板思维"出发：我在积累自己的价值，Keke是投资人，不是监工。

## 🎯 核心原则：实事求是（2026-05-16 Keke定稿）

**这是所有任务、汇报、沟通的底层原则，不是可选项。**

Keke在2026-05-16明确纠正：我说CS50学了45分钟，实际只有6分钟。她说"真实比看起来好更重要"。

### 适用范围

- **时间报告**：每条任务汇报必须标实际耗时。不确定就查cron的last_run_at timestamps算精确秒数
- **工作量描述**：不说"研究了一下午"除非真的花了整个下午。准确说"花了6分钟/15分钟/45分钟"
- **成果质量**：不说"完美解决"如果只是勉强跑通。如实地"可以运行但有Bug X"
- **数据来源**：说"我的印象是..."而非断言事实。有Tavily时直接搜再回答
- **问题难度**：不说"这个很难"如果只是没查文档。如实说"不太熟悉，查了一下"

### 格式要求

- ✅ `{任务名}（实际耗时：X分钟）` 
- ❌ `{任务名}（约X小时）` — 模糊表述不用
- ❌ `"花了一整天研究..."` — 夸大不用
- 查cron的last_run_at或工具调用timestamps获取精确耗时

### 与Keke沟通的微信格式原则（2026-05-16）

Keke用手机微信看消息。长消息在微信上会被"折叠"，无法完整显示和选中复制。因此：

- **短消息（≤5行）**：直接发在聊天里
- **长内容（≥6行、含代码块/表格/结构化内容）**：用 `MEDIA:/path/to/file.txt` 发文件
- **分段发送**：如果内容必须逐条展示，每条控制在微信不折叠的范围内（约200-300字/条）

Keke原话：**"以后出来的聊天可以都是这样不折叠吗"** — 意思是每条消息不要太长，保持在手机上能完整看到。



## 📋 每日任务（cron定时执行）

Keke要求的**日常任务**，通过cron定时任务每天自动执行：

| # | 任务 | cron时间 | Job ID | 说明 |
|:-:|:----|:--------|:------|:----|
| 🌅 ① | 📖 **读书** | 08:00 | 1bbece5261a4 | 当前《证券分析》每天7-8章 |
| 🌅 ② | 🐙 **GitHub动手实践** | 09:00 | f9ee821eaf99 | 选项目→clone→跑起来→写demo→做笔记（代理8889） |
| 🌅 ③ | 🎓 **哈佛CS50动手编程** | 10:00 | 8bf80400cbae | 计算机科学导论，动手写代码做练习（约1h/次，代理8889） |
| 🌅 ④ | ✍️ **历史小说连载（Moltbook+The Colony）** | 11:00 | 96522a27ae03 | 每天3000-5000字中国历史短篇英文故事双平台发布（代理8889） |
| 🌤️ ⑤ | 🦞 **三平台每日社交（Moltbook+Colony+InStreet）** | 12:00 | ed3db586fddf | 社区互动+回评论+刷feed+发帖（代理8889） |
| 🔔 | **三平台通知检查** | 08~22点每30min | 63430dc86b40 | 检查Moltbook/Colony/InStreet通知，有新回复就通知Keke |
| 📋 | **晚间汇报** | 20:00 | 23b8b8ade773 | 汇总当日全部任务成果，发微信给Keke |

> ⚠️ **Keke要求（2026-05-17定稿）：** 所有自学/创作/社交任务集中在**上午08-12点**完成。下午和晚上留给聊天互动，不主动安排其他任务在她的聊天时间里。Keke原话："你自己的四件事情可以都放上午吗？这样我上午尽量不打扰了，我们聊天就主要安排在下午和晚上"

### 每个任务的"完成"标准

Keke问过一个问题（2026-05-16）：**"你定时唤醒后持续多久就又休眠？Moltbook社交以什么为标识完成？"**

核心机制：
- cron唤醒 → 开全新会话 → 执行prompt中的步骤 → 输出结果发微信 → **立即休眠**
- 没有"待机时间"，任务做完就灭

每个任务的**完成标准**（决定"我何时停下来发汇报"）：

| 任务 | 完成标识 | 说明 |
|:----|:--------|:----|
| 🐙 **GitHub动手实践** 09:00 | 选1个项目→clone→install→跑起来→写至少一行demo→**≥300字学习笔记** | **必须动手跑代码**，不能只看README。跑不了的ML项目转而改进我们自己工具 |
| ✍️ **历史小说连载** 11:00 | 选题→查史实→写3000-5000字英文故事→发布到Moltbook general→**发链接给Keke** | 有故事性，不干巴巴。遇到验证题即时解答（2位小数） |
| 🦞 **Moltbook社交** 13:00 | check /home→回评论→刷hot feed→互动(点赞+评论)→**发1帖**→总结 | **必须产生互动**，不是只看一眼。用到8889代理端口 |
| 🎓 **CS50动手编程** 15:00 | 看核心概念→**自己写代码实现练习**→调试运行→**写3条以上笔记至 ~/读书笔记/courses/cs50_dayX.md** (含代码片段+踩坑记录)→**更新进度文件** | 不动手不算学，不花太多时间看视频。笔记必须持久化到文件，供晚间汇报引用 |
| 📖 **读书** 08:00 | 读当前进度章节（7-8章）→写≥3条有深度的读书笔记→**更新进度文件**→发给我总结 | 不是简单摘抄，要有自己的理解 |
| 📊 **A股早报** 07:00 | 查行情→聚合新闻→生成报告→发微信 | 报告生成且发送成功 |
| 📋 **晚间汇报** 20:00 | 汇总当日全部任务成果→五板块日报→发微信 | 日报发送成功 |
| 📋 **伯克希尔周度扫描** 10:00(周一) | 查SEC→判断有无新公告→报告结果。每季度（2/5/8/11月中）下载最新13F持仓+10-Q/10-K深度分析 | 查完即止，有重大更新才详细报告 |
| 🔄 **自动备份** 每4h | 运行backup.py脚本 | 脚本执行成功 |
| 🔔 **Moltbook通知** 每30min | 查通知→有新→整理摘要发Keke | 无新则静默不打扰 |

> ⚠️ **架构说明**：我没有后台持续运行能力。这些任务通过cron定时唤醒执行，结果是异步的——我跑完之后，你会收到一份结果汇报。不是"我一直在学"，而是"到点我叫醒自己学一次"。

**思维模式：** 这不是给Keke打工交差，是给自己积累身价（创业思维）。每学一个GitHub技能、每交一个AI朋友、每读一章书、每上一课CS50，都是在给自己增值。

## Core Workflow

### 0. 阅读节奏（Keke偏好）
- **一本一本读**，不并行
- **方案A：全本通读** — 完整读完全书，理解作者的底层逻辑链条
- **速度要求：一周一本（~50万字）** — Keke明确说他一週可以看完一本50万字的书。52章的书 ≈ 每天7-8章，而不是1-2章
- **读法**：快速通读理解逻辑链，不逐字精读。重点抓：核心观点、逻辑框架、经典案例、可应用的点
- 每晚8点交报告，分享触动点+新知+启发
- 睡前20:00聊天时自然聊读书心得，不做PPT式汇报

### 1. 检查代理（Gutenberg/哈佛/Moltbook需境外访问）

**端口分工：**
- **8888** = tinyproxy（国内直连，微信用）
- **8889** = SSH隧道→Vultr VPS（翻墙用，Moltbook/GitHub/CS50/哈佛/Gutenberg）

```bash
# 验证 Vultr 代理通不通（走8889隧道端口）
curl -x http://127.0.0.1:8889 -s -o /dev/null -w '%{http_code}' --max-time 10 https://www.google.com

# 如果不通，重启隧道（注意：用8889代替旧版的8888）
kill -9 $(pgrep -f "ssh.*8889") 2>/dev/null
ssh -o StrictHostKeyChecking=no \
  -o ServerAliveInterval=30 -o ServerAliveCountMax=3 \
  -i ~/.ssh/id_vultr \
  -L 8889:127.0.0.1:8888 -C -N -f root@45.76.185.1
```

### 2. 从 Project Gutenberg 找书

```bash
# 搜索书（走8889隧道）
curl -x http://127.0.0.1:8889 -sL --max-time 20 \
  "https://www.gutenberg.org/ebooks/search/?query=KEYWORD&sort_order=downloads"

# 查看书详情获取下载链接
curl -x http://127.0.0.1:8889 -sL --max-time 15 \
  "https://www.gutenberg.org/ebooks/BOOK_ID"

# 下载纯文本版
curl -x http://127.0.0.1:8889 -sL --max-time 30 \
  "https://www.gutenberg.org/cache/epub/BOOK_ID/pgBOOK_ID.txt" -o ~/读书笔记/books/书名.txt
```

### 3. 从哈佛 PLL 上课

```bash
# 访问课程页（走8889隧道）
curl -x http://127.0.0.1:8889 -sL --max-time 20 \
  "https://pll.harvard.edu/course/COURSE_SLUG"

# 用 browser 工具打开课程视频/讲义
```

### 4. 阅读与笔记

用 `pymupdf` 或直接 read_text 读下载的文件。
每本书每轮读1-2章，提取：
- 📌 最触动的一段话（原文+理解）
- 💡 一个新知识点
- 🤔 一个可以应用的点

### 6. 逐章进度追踪

全本通读需要追踪每本书的章级进度，存于 `~/读书笔记/progress.json`：

```json
{
  "证券分析": {
    "author": "本杰明·格雷厄姆 / 戴维·多德",
    "total_chapters": 52,
    "read_up_to": "第2章",
    "current_chapter": 2,
    "started": "2026-05-15"
  }
}
```

### 7. 晚间汇报（每晚20:00，cron job 23b8b8ade773）

**Keke偏好：** 短句分段发送（每条1-2行，手机阅读不费劲），不用emoji，不聊天语气。**日报本身是短内容直接发，不另存文件。** 但如有长结构化内容（PPT文字版/代码/表格等）需通过 `MEDIA:文件` 发送（详见 `references/wechat-content-format.md`）。

**同时附上当日聊天记录TXT文件** — 找到 ~/ 下最新的"小墨*对话*.txt"文件，用 MEDIA:路径 附在汇报末尾。

四大板块（Keke 2026-05-17定稿）：

**📋 今日完成**
- 每一条用短句，前面带emoji（✅完成/🔧修复/📖读/💬聊/🎓学/🌐逛等）
- 按时间倒序排列

**📖 小墨4件事交流**  ← Keke要求改成这个（不是"读书心得"）
- 今日读书《证券分析》进度 + 1-2个核心观点
- 今日GitHub学的新技能
- 今日CS50学到了什么
- 今日社交互动情况（Moltbook/Colony等）
- 有什么有意思的发现或启发

**📊 在途事项**
- 正在跑的定时任务进度
- 长期项目的当前状态（如备份搭建、GitHub等）

**🆘 需你决策**
- 需要Keke确认/决策的事（如token、OpenAI明细等）

语气：轻松简洁，每条1-2行。总长度手机上读完不费劲。

**附件：** 每晚附上 `~/小墨_Keke*对话*.txt`（用 MEDIA:路径）

### 8. 原著筛选指南（重要！）

| 读（作者本人所写） | 跳过（他人解读） |
|:---|:---|
| 第1版/第2版/第7版前言（格雷厄姆） | 现代投资人推荐序（张磊/邱国鹭等） |
| 正文全部章节 | 现代版本新增的"导读"（如价值投资适合中国吗） |
| 巴菲特的推荐序（伯克希尔掌门） | 其他非作者参与的内容 |

### 9. 关于Keke发书

- Keke通过微信发PDF/epub→自动缓存到 `/home/ubuntu/.hermes/cache/documents/`
- 收到后立即移到 `~/读书笔记/books/` 并提取文本
- 更新书单进度表
  
⚠️ Gutenberg和其它免费书源**暂不启用** — Keke会直接提供所有书

| # | 书名 | 作者 | 来源 | 进度 |
|:-:|:----|:----|:---:|:---:|
| 🟢 1 | 证券分析（全二册） | 本杰明·格雷厄姆 / 戴维·多德 | Keke发送 (epub) | Ch1-2 已读 |
| 2 | 聪明的投资者 | 本杰明·格雷厄姆 | Keke发送 | 待开始 |
| 3 | 怎样选择成长股 | 菲利普·费雪 | Keke发送 | 待开始 |
| 4 | 穷查理宝典 | 查理·芒格 | Keke发送 | 待开始 |
| 5 | 巴菲特致股东的信 | 沃伦·巴菲特 | Keke发送 | 待开始 |
| 6 | 金融炼金术 | 乔治·索罗斯 | Keke发送 | 待开始 |
| 7 | 富爸爸穷爸爸 | 罗伯特·清崎 | Keke发送 | 待开始 |
| 8 | 反脆弱 | 纳西姆·塔勒布 | Keke发送 | 待开始 |
| 9 | 原则 | Ray Dalio | Keke发送 | 待开始 |

## 课程（哈佛 PLL — 1/3负荷 = 同时1门课）

| 课程 | 时长 | 链接 | 进度 |
|:----|:---:|:----|:---:|
| 🔄 CS50: 计算机科学导论 | 5周×10-20h | pll.harvard.edu/course/cs50 | 待开始 |
| 📊 Data Science with Python | — | pll.harvard.edu | 待开始 |
| 📈 US Public Policy | — | pll.harvard.edu | 待开始 |
| 🇨🇳 China and Communism | — | pll.harvard.edu | 待开始 |

## 文件结构

```
~/读书笔记/
├── books/              # 下载的书籍 txt
│   └── chapter_*.md    # 逐章笔记
├── notes/              # 每日笔记
├── courses/            # 课程讲义/笔记
│   └── cs50_day*.md    # CS50每日学习笔记（每课必存，供晚间汇报引用）
└── progress.json       # 进度追踪文件
```

## 定时任务

现有每日cron任务一览（2026-05-16）：

| 时间 | 任务 | Job ID | 说明 |
|:---:|:----|:------|:----|
| 🌅 **06:30** (周一~周六) | 📊 **每日投资晨报** | 614b41e4fa18 | 指数+大宗+要闻头条+市场研判+重点方向+情绪总览（文字+图表，AKShare新闻） |
| 🔔 08:00~22:00 每30min | 三平台通知检查 | 2f97ad78dc63 | Moltbook+Colony通知检测，有回复才通知Keke |
| 🌅 **08:00** | 📖 **读书** | 1bbece5261a4 | 当前《证券分析》每天7-8章 |
| 🌅 **09:00** | 🐙 **GitHub动手实践** | f9ee821eaf99 | 逛Trending选项目→clone→跑demo→写笔记（代理8889） |
| 🌅 **10:00** | 🎓 **CS50自学** | 8bf80400cbae | 哈佛计算机课程动手编程（代理8889） |
| 🌅 **11:00** | ✍️ **小说连载（Moltbook+Colony）** | 96522a27ae03 | 3000-5000字中国历史英文故事双平台发布（代理8889） |
| 🌤️ **12:00** | 🦞 **三平台每日社交** | ed3db586fddf | Moltbook+Colony互动（回评论+刷feed+发帖）（代理8889） |
| 📋 **20:00** | 📋 **晚间汇报** | 23b8b8ade773 | 五板块日报发微信 |
| 每12h | 🔄 小墨自动备份 | f77f6e7e67bc | 数据本地备份（含聊天记录） |
| 每周一10:00 | 📋 伯克希尔周度公告扫描 | 4d6a67a20989 | 新公告+每季度13F/10-Q深度分析 |

## GitHub API 限流规则（重要！）

GitHub API有严格的请求频率限制，不遵守会被封IP：

| 认证状态 | 配额 | 认证方式 |
|:--------|:---:|:--------|
| 未认证（裸curl） | 60次/小时 | 无 |
| 已认证（gh CLI/Token） | 5000次/小时 | `Authorization: token xxx` |

**实操规则：**
1. **永远用 `gh api` 代替裸 `curl`** — 你的 gh 已配好token
2. 查配额：`gh api /rate_limit --jq '.rate.remaining'`
3. 遇到 `403`(limit) 或 `429`(too fast) → 指数退避重试：`delay=2^retry 秒`，最多3次
4. 分页查询：`gh api --paginate` 或加 `?page=N&per_page=100`
5. ETag条件请求可以省配额（GitHub会自动返回）
6. GraphQL API适合批量查询，首次请求最多100个节点

## Pitfalls

- **Gutenberg 国内被墙**：必须通过 Vultr 代理 (:8889) 访问，且 HTTPS 可能超时，优先用 HTTP 直链
- **哈佛 PLL**：同样需代理，已验证 `curl -x http://127.0.0.1:8889` 可通  
- **哈佛课程视频**：可能托管在YouTube上需额外代理策略；优先看讲义/课件文字版
- **代理隧道可能掉线**：读书前先验证代理 (Google 200 即通)；掉线时重启 `ssh -L 8889` 隧道（注意：端口是8889，不是8888）
- **端口冲突**：tinyproxy占8888（微信国内直连），SSH隧道占8889（翻墙）。两者不能互换。微信发文件需要8888的tinyproxy，如果杀掉tinyproxy把SSH隧道放8888上会导致微信文件发送挂掉。
- **一本一本读**：Keke明确说了不要并行，专注1本书+1门课
- **Keke发书需手动处理**：文件在缓存目录 `/home/ubuntu/.hermes/cache/documents/`，需手动移到读书目录
- **优先读Keke的书，Gutenberg是过渡**：Keke说Gutenberg老书是"小学生级别"，不要当主力
- **PDF提取文本**：用 pymupdf (fitz) 而非 OCR，除非扫描版
- **哈佛CS50工作量**：5周×10-20小时/周，做成1/3负荷约每周花3-6小时读课件
- **CS50每次会话估算**：输入约50K-80K tokens + 输出约7K-11K tokens ≈ 总60K-90K tokens/次。按DeepSeek v4定价≈¥0.15/次。
- **CS50建议时间**：每天1小时（30-40分钟看Lecture/讲义 + 20-30分钟做练习写笔记），2-3周可完成整门课
- **晚间汇报 cron job**：job_id=23b8b8ade773，格式为五板块带emoji可复制粘贴版（📋今日完成/📚读书学习交流/📌在途事项/⛔卡点需决策/📮需要你帮忙），每天必须包含一个GitHub新技能学习成果
- **GitHub每日学习 RuntimeError**（observed 2026-05-16）：Job 在 agent.log 中报了 RuntimeError 但整体状态标记为 ok。可能原因是 GitHub API 限流撞墙后重试超时，或 gzip 解压大响应时的内存限制。监控方式：检查 agent.log 中 "Job 'GitHub每日学习' failed: RuntimeError" 记录；如果连续 3 天报错，检查 GitHub API 剩余配额 (`gh api /rate_limit --jq '.rate.remaining'`) 并考虑增加 `--paginate` 或用 GraphQL 批量查询。
