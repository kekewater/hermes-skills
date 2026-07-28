#!/usr/bin/env python3
"""
微信读书笔记每日同步脚本 — 自动导出最近更新过的书的笔记。
适用于 cron 定时调度。

用法：
  python3 daily_sync_weread.py

环境变量：
  WEREAD_API_KEY    必需，微信读书 API Key
  WEREAD_NOTES_DIR  可选，输出目录（默认 ~/.weread-notes/）
"""
import os, sys, time
from pathlib import Path
from datetime import datetime

# 确保在脚本所在目录，以便导入 sibling 模块
sys.path.insert(0, str(Path(__file__).parent))
from export_weread_notes import api_call, export_book, NOTES_DIR


def main():
    print(f"📚 读书小记每日同步 — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()

    # 获取全部有笔记的书
    data = api_call("/user/notebooks", {"count": 2000})
    books = data.get("books", [])
    total = data.get("totalBookCount", len(books))
    if data.get("hasMore") and total > 2000:
        data = api_call("/user/notebooks", {"count": total})
        books = data.get("books", [])
    print(f"共 {len(books)} 本有笔记的书（总计 {total} 本）")

    # 筛选最近 48 小时内有更新的
    now = time.time()
    cutoff = now - 48 * 3600
    updated = []

    for b in books:
        sort_time = b.get("sort", 0)
        if sort_time >= cutoff:
            book = b.get("book", {})
            title = book.get("title", "?")
            bm = b.get("bookmarkCount", 0)
            nc = b.get("noteCount", 0)
            rc = b.get("reviewCount", 0)
            update_time = datetime.fromtimestamp(sort_time).strftime("%m-%d %H:%M")
            updated.append({
                "book": book, "title": title,
                "bm": bm, "nc": nc, "rc": rc,
                "update_time": update_time,
            })

    if not updated:
        print("\n✅ 没有最近更新的书，无需同步")
        return

    print(f"\n🔄 检测到 {len(updated)} 本最近有更新的书：")
    for u in updated:
        print(f"  《{u['title']}》 — 最后更新 {u['update_time']}")

    print("\n--- 开始同步 ---")
    success = 0
    failed = 0
    for u in updated:
        print(f"\n📖 正在导出《{u['title']}》...", end=" ")
        try:
            result = export_book(u["book"])
            if result:
                print("✅")
                success += 1
            else:
                print("⏭️ 跳过（无内容）")
                failed += 1
        except Exception as e:
            print(f"❌ {e}")
            failed += 1

    print(f"\n{'='*40}")
    print(f"📊 同步完成：成功 {success} 本，失败 {failed} 本")
    print(f"📁 笔记目录：{NOTES_DIR}")


if __name__ == "__main__":
    main()
