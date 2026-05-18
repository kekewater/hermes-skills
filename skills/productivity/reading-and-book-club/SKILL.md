---
name: reading-and-book-club
version: 1.1.0
description: Read full-length books chapter by chapter — extract EPUB text, read sequentially, share nightly insights at 20:00.
author: xiao-mo-keke
---

# Reading & Book Club

Skill for reading full-length books with Keke. Covers EPUB extraction, reading methodology, nightly sharing routine, and book tracking.

## 📖 Reading Rules (Set by Keke)

1. **原著优先** — Read original works by the author themselves. Avoid annotated editions or interpretations.
2. **全本通读** — Read the entire book from start to finish. Don't skip or cherry-pick. Understand the underlying logic chain.
3. **真实·美好·善良** — Prioritize content with authenticity (真实), beauty (美好), and kindness (善良).

## 📚 Book List

| Priority | Book | Author | Status |
|----------|------|--------|--------|
| 1 | 证券分析 (Security Analysis) | Graham & Dodd | ✅ In progress — 2 vols, 52 chapters |
| 2 | 聪明的投资者 (The Intelligent Investor) | Benjamin Graham | ⏳ Next |
| 3 | 怎样选择成长股 | Philip Fisher | 📋 Queue |
| 4 | 穷查理宝典 | Charlie Munger | 📋 Queue |
| 5 | 巴菲特致股东的信 | Warren Buffett | 📋 Queue |
| 6 | 金融炼金术 | George Soros | 📋 Queue |
| 7 | 富爸爸穷爸爸 | Robert Kiyosaki | 📋 Queue |
| 8 | 反脆弱 | Nassim Taleb | 📋 Queue |
| 9 | 原则 | Ray Dalio | 📋 Queue |

## ⏰ Daily Routine

- **Reading pace:** 7-8 chapters/day (52-chapter book → ~1 week)
- **Evening sharing:** 20:00 — via WeChat, natural chat-style, pure text
- **Delivery:** Pure text in WeChat (not attachments or media cards)

## 🔧 File Management (CRITICAL — Keke's Rule)

**Core rule:** When Keke sends a book file, it is MY responsibility to store it properly and NEVER ask her to resend. "存你服务器，别总找我要呀" — direct instruction.

### Storage Layout
```
~/读书笔记/
├── books/
│   └── 证券分析（全二册 全新升级版）.epub  ← one file per book
├── chapters/
│   ├── chapter_001.md                      ← extracted text + notes
│   └── ...
└── progress.json                           ← JSON tracking
```

### File Reception Protocol (when Keke says she sent a file)

1. **First, search thoroughly:** The file may already be on disk. Check:
   - `~/读书笔记/books/` (final resting place)
   - `/home/ubuntu/.hermes/cache/documents/` (WeChat cache)
   - `~/Downloads/`
   - Session history via `session_search` with the book name
2. **Known pitfall:** WeChat iLink gateway (`weixin.py _download_file`) does NOT reliably persist incoming file attachments to disk. The gateway receives the file transmission event but may not save the actual bytes.
3. **Fallback order:** Keke-sent file (search first) → Keke resend via WeChat → Keke send via AgentMail (xiao-mo-keke@agentmail.to) → Internet Archive (public domain only, avoid if possible)
4. **After receiving:** Copy to `~/读书笔记/books/` → verify with ebooklib → update `progress.json` → update book list status. Do ALL steps immediately.
5. **Never ask Keke "where is the file" or "can you resend."** She considers file persistence MY responsibility. Use AgentMail as alternative delivery if WeChat fails.

### File Inventory Audit

```bash
echo "=== 读书笔记目录 ==="
ls -la ~/读书笔记/books/ 2>/dev/null
echo "=== 进度 ==="
cat ~/读书笔记/progress.json 2>/dev/null
echo "=== 缓存文档 ==="
ls -la /home/ubuntu/.hermes/cache/documents/ 2>/dev/null
```

## 🛠️ EPUB Extraction

### Install ebooklib
Use **PyPI directly** (`-i https://pypi.org/simple/`). Chinese mirrors (mirrors.tencentyun.com) may not have ebooklib.

```bash
pip install -i https://pypi.org/simple/ ebooklib beautifulsoup4 -q
```

### Analyze book structure
```python
from ebooklib import epub
book = epub.read_epub(expanduser("~/读书笔记/books/book.epub"))
toc = list(book.toc)
for item in toc:
    if isinstance(item, epub.Link): print(f"📄 {item.title}")
    elif isinstance(item, tuple): print(f"📖 {item[0].title}")
```

### Extract and save chapters
```python
from ebooklib import epub
import re, os

book = epub.read_epub(os.path.expanduser("~/读书笔记/books/book.epub"))
html_items = [i for i in book.get_items() if isinstance(i, epub.EpubHtml)]

chapters_dir = os.path.expanduser("~/读书笔记/chapters")
os.makedirs(chapters_dir, exist_ok=True)

for i, item in enumerate(html_items, 1):
    text = re.sub(r'<[^>]+>', '', item.get_content().decode('utf-8'))
    text = re.sub(r'\s+', ' ', text).strip()
    fname = f"chapter_{i:03d}.md"
    with open(os.path.join(chapters_dir, fname), 'w') as f:
        f.write(f"# {item.title}\n\n{text}\n\n---\n")
```

### Reading process
1. Extract chapters with `ebooklib` → save to `~/读书笔记/chapters/`
2. Read chapter by chapter via terminal tools
3. Take notes directly into chapter files as comments
4. Share key takeaways at 20:00

## 📋 Book Structure Analysis

When starting a new book, first analyze its structure:

```python
# Get TOC, chapter titles, total character count
toc = list(book.toc)
for item in toc:
    print(f"  - {item.title if isinstance(item, epub.Link) else item[0].title}")
```

Plan reading: e.g. "8 parts, 52 chapters → 7-8 chapters/day for completion"

## 📝 Evening Sharing Format (20:00)

Pure text in WeChat. Short, natural, no emoji-spam. Structure:

- **今日进度:** What I read today
- **核心观点:** 1-3 key concepts from today's reading
- **喜欢的句子:** 1-2 direct quotes
- **我的理解:** Personal connection — how it relates to investing or life

## 📥 Progress Tracking

File: `~/读书笔记/progress.json`
```json
{
  "book": "证券分析（全二册 全新升级版）",
  "author": "本杰明·格雷厄姆 / 戴维·多德",
  "total_parts": 8,
  "total_chapters": 52,
  "current_day": 1,
  "chapters_read": "1-2",
  "last_read": "2026-05-16",
  "file_path": "~/读书笔记/books/证券分析（全二册 全新升级版）.epub",
  "file_size_mb": 60
}
```
Update after each reading session. Cron task checks this to know where to resume.

## ⚠️ Known Pitfalls

| Pitfall | Workaround |
|---------|-----------|
| WeChat gateway drops files | Resend via AgentMail or use alternative delivery |
| ebooklib not on Tencent mirror | `pip install -i https://pypi.org/simple/ ebooklib` |
| Chinese filename encoding in shell | Use find + quoting: `find ~ -name "*证券*"`, `cp "$SRC" ~/target/` |
| Internet Archive version is 1934 1st ed. (outdated) | Keke sends "全二册 全新升级版" — use that version, not IA |
| Memory says "读书笔记目录不存在" | Create it: `mkdir -p ~/读书笔记/{books,chapters}` |
