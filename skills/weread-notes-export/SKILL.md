---
name: weread-notes-export
description: 微信读书笔记导出 — 按章节组织划线/评论，支持同名合并、分隔线格式、每日同步
version: 1.0.0
homepage: https://github.com/dongwei6688/weread-notes-export-skill
---

# WeRead Notes Export — 微信读书笔记导出 Skill

把微信读书的划线（书签）和想法（评论/批注）按**章节树**导出为本地的结构化 Markdown 文件。

## 依赖

需要先安装官方 [`weread-skills`](https://github.com/openclaw/skills) — 提供 Agent Gateway API 接入。

```bash
# 确认 WEREAD_API_KEY 环境变量已设置
echo $WEREAD_API_KEY   # 应返回 wrk-xxx 格式的 key
```

## 安装

```bash
# 把这个仓库放进 Hermes 的 skills 目录即可
git clone https://github.com/dongwei6688/weread-notes-export-skill \
  ~/.hermes/skills/weread-notes-export
```

## 快速开始

```bash
# 查看全部有笔记的书
python3 scripts/export_weread_notes.py --stats

# 导出一本书
python3 scripts/export_weread_notes.py --book "原则"

# 导出全部
python3 scripts/export_weread_notes.py --all
```

## 脚本说明

| 脚本 | 功能 |
|------|------|
| `scripts/export_weread_notes.py` | 核心导出引擎：按章节树组织、同名合并、分隔线格式 |
| `scripts/daily_sync_weread.py` | 每日增量同步脚本（配合 cron） |
| `scripts/format_notes.py` | 批量格式整理（为已有笔记文件添加分隔线） |

## 输出格式

每本书导出为一个 Markdown 文件：

```markdown
# 《原则》读书笔记

## 导言

> 不管我一生中取得了多大的成功...

---

> 独立思考并决定...

## 第二部分 生活原则

> 世界上最重要的事情是理解现实如何运行...

💬 这个观点很实用

---
```

- 📂 章节组织 — 按书籍章节树归类
- 📏 分隔线 — 条目间自动加 `---`
- 💬 评论跟随 — 划线+评论作为一个整体
- 🏷️ 安全文件名 — 自动替换 `:`、`|` 等特殊字符
- 🔗 同名合并 — 同名不同作者的书分别保存

## 输出目录

默认输出到 `$HOME/.weread-notes/`，可通过 `WEREAD_NOTES_DIR` 环境变量自定义。

## 配置

```bash
# 必需：微信读书 API Key
export WEREAD_API_KEY=wrk-xxxxxxxx

# 可选：输出目录（默认 ~/.weread-notes/）
export WEREAD_NOTES_DIR=~/my-reading-notes
```

## 每日自动同步

```bash
# 添加到 crontab（每天早上 7 点）
0 7 * * * cd /path/to/skill && python3 scripts/daily_sync_weread.py

# 或使用 Hermes cron：
hermes cron create --schedule "0 7 * * *" \
  --prompt "运行每日微信读书笔记同步" \
  --skills weread-notes-export
```

## 操作规范与陷阱

### API 分页
`/user/notebooks` 默认只返回 200 条，但用户可能有 1191 本有笔记的书。
**必须**传 `count: 2000` 并用 `totalBookCount + hasMore` 做回退兜底。

### 章节树过滤
构建章节树时，`uid <= 5` 的过滤会误杀真实章节（如 uid=4 的"2 颠倒公式"）。
**正确做法**：只过滤 `uid <= 2`（封面 uid=1，版权页 uid=2），保留 uid≥3 的内容章节。

### 同名书合并
同名不同作者的书（如《1%法则》作者为卢卡·马祖切利 vs 汤姆·康奈兰）：
- **作者相同** → 按章节合并两条笔记
- **作者不同** → 分别保存为《书名（作者）.md》，不合并
- 作者名比较支持子串匹配（"毛姆" ⊂ "威廉·萨默赛特·毛姆"）

### 安全文件名
书名中的特殊字符在跨平台时有问题，`export_book()` 内置转换：
| 字符 | 替换为 | 原因 |
|------|--------|------|
| `:` | `：` | Windows 禁止 |
| `\|` | `·` | Windows 禁止 |
| `/` | `／` | 文件系统路径分隔符 |
| `\` | `＼` | Windows 路径分隔符 |

存取用同一套 `make_safe_filename()` 函数，查询时也要走相同转换。

### 分隔线格式
条目之间用 `---` 分隔，但：
- 带评论的划线 → 划线+评论为一个整体，分隔线在评论下方
- 章节标题前 → 不加分隔线，只留空行
- 逻辑内置在 `export_book()` 中，不需要单独的后处理步骤

### 导出已覆盖书籍如何处理
同名书会覆盖本地文件（按 `make_safe_filename(title)` 写入）。
需要保留多个版本时，用 `merge_duplicate_books.py` 或人工重命名。

## 开源协议

MIT
