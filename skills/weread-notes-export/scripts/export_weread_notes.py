#!/usr/bin/env python3
"""
微信读书笔记导出工具 — 把划线、想法按章节导出为本地的结构化 Markdown 文件。

用法：
  python3 export_weread_notes.py --book "原则"
  python3 export_weread_notes.py --book "27094128"
  python3 export_weread_notes.py --list           # 列出有笔记的书
  python3 export_weread_notes.py --all            # 导出全部
  python3 export_weread_notes.py --stats          # 统计
  python3 export_weread_notes.py --recent         # 查看最近更新的书

环境变量：
  WEREAD_API_KEY    必需，微信读书 API Key，格式 wrk-xxx
  WEREAD_NOTES_DIR  可选，输出目录（默认 ~/.weread-notes/）
"""
import json, os, sys, time, urllib.request
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

# ── 配置 ──────────────────────────────────────────────────────────────
API_URL = "https://i.weread.qq.com/api/agent/gateway"
SKILL_VERSION = "1.0.0"

# 输出目录：优先读环境变量，默认 ~/.weread-notes/
DEFAULT_NOTES_DIR = Path.home() / ".weread-notes"
NOTES_DIR = Path(os.environ.get("WEREAD_NOTES_DIR", str(DEFAULT_NOTES_DIR)))


# ── API 调用 ──────────────────────────────────────────────────────────
def _get_api_key():
    """获取 WEREAD_API_KEY"""
    key = os.environ.get("WEREAD_API_KEY", "")
    if not key:
        print("❌ 请设置 WEREAD_API_KEY 环境变量")
        print("   格式：export WEREAD_API_KEY=wrk-xxxxxxxx")
        sys.exit(1)
    return key


def api_call(api_name, params=None):
    """调用微信读书 Agent Gateway API"""
    body = {"api_name": api_name, "skill_version": SKILL_VERSION}
    if params:
        body.update(params)
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {_get_api_key()}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


# ── 文件名安全转换 ──────────────────────────────────────────────────
def make_safe_filename(title):
    """将书名转为安全的文件名（存和查用同一套规则）"""
    safe = title.replace("/", "／")
    safe = safe.replace("\\", "＼")
    safe = safe.replace(":", "：")
    safe = safe.replace("|", "·")
    return safe


# ── 数据获取 ──────────────────────────────────────────────────────────
def get_notebooks(max_count=2000):
    """获取有笔记的书列表（自动拉取全部）"""
    data = api_call("/user/notebooks", {"count": max_count})
    books = data.get("books", [])
    total = data.get("totalBookCount", len(books))
    if data.get("hasMore") and total > max_count:
        data = api_call("/user/notebooks", {"count": total})
        books = data.get("books", [])
    return books


def get_bookmarks(book_id):
    """获取划线笔记"""
    data = api_call("/book/bookmarklist", {"bookId": str(book_id)})
    return data.get("updated", [])


def get_reviews(book_id):
    """获取评论/想法"""
    data = api_call("/review/list/mine", {"bookid": str(book_id)})
    return data.get("reviews", [])


# ── 核心导出逻辑 ────────────────────────────────────────────────────
def export_book(book_info):
    """导出一本书的完整笔记"""
    title = book_info.get("title", "未知书名")
    author = book_info.get("author", "")
    book_id = str(book_info.get("bookId", ""))

    print(f"📖 正在导出《{title}》...", end=" ", flush=True)

    bookmarks = get_bookmarks(book_id)
    reviews = get_reviews(book_id)

    if not bookmarks and not reviews:
        print("跳过（无内容）")
        return False

    # ── 获取章节映射 ──
    chapter_map = {}
    try:
        ch_data = api_call("/book/chapterinfo", {"bookId": book_id})
        current_part = ""
        for ch in ch_data.get("chapters", []):
            uid = ch.get("chapterUid")
            ch_title = ch.get("title", "")
            level = ch.get("level", 0)
            if not uid or not ch_title:
                continue
            if level == 1:
                current_part = ch_title
                chapter_map[uid] = ch_title
            elif level == 2 and current_part:
                chapter_map[uid] = f"{current_part} > {ch_title}"
            else:
                chapter_map[uid] = ch_title
    except Exception:
        pass

    # 构建章节名称 → 完整路径的反向映射
    chapter_path_by_name = {}
    for uid, full_path in chapter_map.items():
        leaf_name = full_path.split(" > ")[-1] if " > " in full_path else full_path
        chapter_path_by_name[leaf_name] = full_path

    # ── 构建章节树（仅过滤封面/版权页） ──
    chapter_tree = OrderedDict()
    chapter_info_by_name = {}
    try:
        ch_data = api_call("/book/chapterinfo", {"bookId": book_id})
        current_part = ""
        for ch in ch_data.get("chapters", []):
            uid = ch.get("chapterUid")
            ch_title = ch.get("title", "")
            level = ch.get("level", 0)
            if not uid or not ch_title or uid <= 2:  # 仅过滤封面(1)和版权页(2)
                continue
            if level == 1:
                current_part = ch_title
                full_path = ch_title
            elif level == 2 and current_part:
                full_path = f"{current_part} > {ch_title}"
            else:
                full_path = ch_title
            chapter_tree[full_path] = []
            chapter_info_by_name[ch_title] = (uid, full_path)
    except Exception:
        pass

    # ── 按章节放置划线和评论 ──
    review_map = {}
    for rv in reviews:
        r = rv.get("review", {})
        rid = rv.get("reviewId", "0")
        review_map[rid] = {
            "abstract": r.get("abstract", "").strip(),
            "content": r.get("content", "").strip(),
            "chapter": r.get("chapterName", ""),
            "chapterUid": r.get("chapterUid", ""),
            "chapterTitle": r.get("chapterTitle", ""),
        }

    matched_ids = set()

    for bm in bookmarks:
        text = bm.get("markText", "").strip()
        ch_uid = bm.get("chapterUid", "")
        rng = bm.get("range", "")
        if not text:
            continue

        # 用 chapter_map 定位章节
        target_chapter = None
        ch_name = chapter_map.get(ch_uid, "")
        if ch_name and ch_name in chapter_tree:
            target_chapter = ch_name
        elif ch_name:
            for tree_path in chapter_tree:
                if tree_path.endswith(ch_name) or ch_name.endswith(tree_path):
                    target_chapter = tree_path
                    break

        if not target_chapter:
            target_chapter = "其他"

        item = {"type": "bookmark", "text": text, "range": rng}

        # 匹配评论
        for rid, rv in list(review_map.items()):
            if rid in matched_ids or not rv["abstract"]:
                continue
            if (rv["abstract"][:30] == text[:30]
                or (len(rv["abstract"]) > 5 and rv["abstract"] in text)
                or (len(text) > 5 and text in rv["abstract"])):
                if rv["content"]:
                    item["comment"] = rv["content"]
                matched_ids.add(rid)
                break

        chapter_tree.setdefault(target_chapter, []).append(item)

    # ── 处理未匹配的独立评论 ──
    for rid, rv in review_map.items():
        if rid in matched_ids or not rv["content"]:
            continue
        ch_name = rv["chapter"]
        abstract = rv["abstract"]

        target = None

        # 方式0：评论的 chapterUid 直接查章节树
        ch_uid = rv.get("chapterUid", "")
        if ch_uid and ch_uid in chapter_map:
            mapped_path = chapter_map[ch_uid]
            if mapped_path in chapter_tree:
                target = mapped_path

        # 方式1：评论的章节名映射到完整路径
        if not target:
            full_path = chapter_path_by_name.get(ch_name)
            if full_path and full_path in chapter_tree:
                target = full_path

        # 方式2：评论的 abstract 是章标题
        if not target and abstract:
            norm_abs = abstract.replace("\u3000", " ").replace("\t", " ").strip()
            for tree_title, (uid, path) in chapter_info_by_name.items():
                norm_title = tree_title.replace("\u3000", " ").replace("\t", " ").strip()
                if norm_abs == norm_title or norm_abs in norm_title or norm_title in norm_abs:
                    target = path
                    break

        # 方式3：模糊匹配章节名
        if not target:
            for tree_path in chapter_tree:
                if ch_name and (tree_path.endswith(ch_name) or ch_name in tree_path):
                    target = tree_path
                    break

        if not target:
            target = "其他"

        chapter_tree.setdefault(target, []).append({
            "type": "review_only",
            "abstract": abstract,
            "content": rv["content"],
        })

    # ── 同章内按 range 排序 ──
    for path, items in chapter_tree.items():
        items.sort(key=lambda x: (
            int(x.get("range", "0").split("-")[0]) if x.get("range") and "-" in x.get("range", "") else 999999
        ))

    # ── 生成 Markdown（条目间加分隔线） ──
    lines = [f"# 《{title}》读书笔记", f""]
    if author:
        lines.insert(1, f"作者：{author}")

    for ch_name, items in chapter_tree.items():
        if not items:
            continue
        lines.append(f"\n## {ch_name}")
        lines.append("")
        for idx, item in enumerate(items):
            is_last = (idx == len(items) - 1)
            if item["type"] == "bookmark":
                lines.append(f"> {item['text']}")
                lines.append("")
                if "comment" in item:
                    lines.append(f"💬 {item['comment']}")
                    lines.append("")
                if not is_last:
                    lines.append("---")
                    lines.append("")
            elif item["type"] == "review_only":
                if item["abstract"]:
                    lines.append(f"> {item['abstract']}")
                    lines.append("")
                lines.append(f"💬 {item['content']}")
                lines.append("")
                if not is_last:
                    lines.append("---")
                    lines.append("")

    # ── 写入文件 ──
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = make_safe_filename(title)
    output_path = NOTES_DIR / f"{safe_name}.md"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    bm_count = len(bookmarks)
    rv_count = len(reviews)
    print(f"✅ {bm_count}划线 + {rv_count}评论 → {output_path.name}")
    return True


# ── 列表与统计 ──────────────────────────────────────────────────────
def list_books(recent=False, days=7):
    """列出有笔记的书"""
    books = get_notebooks()
    if recent:
        now = time.time()
        cutoff = now - days * 86400
        print(f"\n📚 最近{days}天更新过的书（共{len(books)}本有笔记）\n")
        recent_books = []
        for b in books:
            sort_time = b.get("sort", 0)
            if sort_time >= cutoff:
                book = b.get("book", {})
                title = book.get("title", "?")
                author = book.get("author", "")
                bm = b.get("bookmarkCount", 0)
                nc = b.get("noteCount", 0)
                rc = b.get("reviewCount", 0)
                update_time = datetime.fromtimestamp(sort_time).strftime("%m-%d %H:%M")
                recent_books.append((sort_time, title, author, bm, nc, rc, update_time))
        recent_books.sort(reverse=True)
        for i, (st, title, author, bm, nc, rc, ut) in enumerate(recent_books, 1):
            print(f"  {i:3d}. 《{title}》{author}")
            print(f"       划线:{bm}  笔记:{nc}  想法:{rc}  最后更新:{ut}")
        print(f"\n共 {len(recent_books)} 本最近更新")
        return

    print(f"\n📚 有笔记的书共 {len(books)} 本\n")
    for i, b in enumerate(books, 1):
        book = b.get("book", {})
        title = book.get("title", "?")
        author = book.get("author", "")
        bm = b.get("bookmarkCount", 0)
        nc = b.get("noteCount", 0)
        rc = b.get("reviewCount", 0)
        print(f"  {i:3d}. 《{title}》{author}")
        print(f"       划线:{bm}  笔记:{nc}  想法:{rc}")


def stats():
    """统计"""
    books = get_notebooks()
    total_bm = sum(b.get("bookmarkCount", 0) for b in books)
    total_nc = sum(b.get("noteCount", 0) for b in books)
    total_rc = sum(b.get("reviewCount", 0) for b in books)
    print(f"\n📊 微信读书笔记统计")
    print(f"   有笔记的书：{len(books)} 本")
    print(f"   总划线数：{total_bm}")
    print(f"   总笔记数：{total_nc}")
    print(f"   总想法数：{total_rc}")


# ── 导出全部 / 按书名查找 ──────────────────────────────────────────
def export_all():
    """导出全部"""
    books = get_notebooks()
    exported = 0
    for b in books:
        if export_book(b.get("book", {})):
            exported += 1
    print(f"\n✅ 导出完成：{exported}/{len(books)} 本书")


def export_by_title(keyword):
    """按书名/ID 导出"""
    books = get_notebooks()
    for b in books:
        book = b.get("book", {})
        title = book.get("title", "")
        bid = str(book.get("bookId", ""))
        if keyword.lower() in title.lower() or keyword == bid:
            export_book(book)
            return

    # 书架没找到 → 搜书城
    print(f"🔍 书架未找到，尝试搜书城取 bookId...")
    data = api_call("/store/search", {"keyword": keyword, "count": 5})
    for result in data.get("results", []):
        for sb in result.get("books", []):
            bi = sb.get("bookInfo", {})
            bid = str(bi.get("bookId", ""))
            title = bi.get("title", "")
            bm = get_bookmarks(bid)
            rv = get_reviews(bid)
            if bm or rv:
                fake_book = {"bookId": bid, "title": title}
                export_book(fake_book)
                return
            else:
                print(f"  ⚠️ 找到《{title}》（{bid}），但无笔记数据")

    print(f"❌ 未找到《{keyword}》的笔记数据")


# ── 入口 ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    NOTES_DIR.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "--list":
        list_books()
    elif cmd == "--recent":
        list_books(recent=True)
    elif cmd == "--all":
        export_all()
    elif cmd == "--book" and len(sys.argv) > 2:
        export_by_title(sys.argv[2])
    elif cmd == "--stats":
        stats()
    else:
        print(__doc__)
