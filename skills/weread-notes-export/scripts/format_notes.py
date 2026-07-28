#!/usr/bin/env python3
"""
批量给已有读书笔记文件添加分隔线。
用于从旧版本升级时整理已有文件。

用法：
  python3 format_notes.py [--dir 笔记目录]
  # 默认处理 WEREAD_NOTES_DIR 或 ~/.weread-notes/
"""
import os, sys
from pathlib import Path

DEFAULT_DIR = Path(os.environ.get("WEREAD_NOTES_DIR", str(Path.home() / ".weread-notes")))


def add_separators(content):
    lines = content.split("\n")
    result = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("## ") or stripped.startswith("# "):
            result.append(line)
            i += 1
            continue
        if stripped.startswith("> "):
            result.append(line)
            i += 1
            while i < n and not lines[i].strip():
                i += 1
            if i < n and lines[i].strip().startswith("💬"):
                result.append(lines[i])
                i += 1
                while i < n and not lines[i].strip():
                    i += 1
            if i < n:
                next_stripped = lines[i].strip()
                if next_stripped.startswith("## ") or next_stripped.startswith("# "):
                    result.append("")
                else:
                    result.append("")
                    result.append("---")
                    result.append("")
            continue
        result.append(line)
        i += 1
    return "\n".join(result)


def main():
    notes_dir = DEFAULT_DIR
    if len(sys.argv) > 2 and sys.argv[1] == "--dir":
        notes_dir = Path(sys.argv[2])

    if not notes_dir.exists():
        print(f"❌ 目录不存在：{notes_dir}")
        sys.exit(1)

    md_files = sorted(notes_dir.glob("*.md"))
    total = len(md_files)
    ok = 0
    skipped = 0

    print(f"📚 共 {total} 个笔记文件，开始添加分隔线...")

    for f in md_files:
        content = f.read_text(encoding="utf-8")
        if not content.strip() or "\n---\n" in content:
            skipped += 1
            continue
        new_content = add_separators(content)
        if new_content == content:
            skipped += 1
            continue
        f.write_text(new_content, encoding="utf-8")
        ok += 1
        if ok % 200 == 0:
            print(f"  ... 已处理 {ok}/{total}")

    print(f"\n✅ 完成：{ok} 个文件添加分隔线，{skipped} 个跳过")


if __name__ == "__main__":
    main()
