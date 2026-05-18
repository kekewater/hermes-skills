# Backup & Restore Commands Quick Reference (Updated 2026-05-16)

## One-Click Restore (新服务器)

```bash
# 从百度网盘拉最新备份自动恢复
bash ~/.hermes/scripts/restore.sh --from-baidu

# 从本地恢复
bash ~/.hermes/scripts/restore.sh --local

# 从URL下载恢复
bash ~/.hermes/scripts/restore.sh --from-url https://...
```

## Manual Backup

```bash
# Manual full backup
timeout 120 python3 ~/.hermes/scripts/backup.py

# Check latest backup
ls -lh ~/.hermes/backups/ | tail -3

# Preview cleanup (no delete)
python3 ~/.hermes/scripts/cleanup_backups.py

# Apply cleanup
python3 ~/.hermes/scripts/cleanup_backups.py --apply

# Cleanup + Baidu Wangpan
python3 ~/.hermes/scripts/cleanup_backups.py --apply --baidu
```

## Restore (Manual)

```bash
# Extract latest backup
LATEST=$(ls -t ~/.hermes/backups/小墨完整备份_*.tar.gz | head -1)
tar -xzf "$LATEST" -C /

# View backup contents
tar -tzf "$LATEST" | head -20
```

## Setup (One-Time)

```bash
# GitHub push (one-time)
gh auth login
# Creates repo: github.com/kekewater/hermes-backup

# Baidu Wangpan (one-time)
pip3 install bypy
bypy info
# → Visit auth URL → scan QR code → paste code

# Cron job (already configured — backup runs every 4h)
hermes cron list | grep backup
```

## Key Files

| File | Purpose |
|------|---------|
| `~/.hermes/scripts/backup.py` | Main backup script (v3.0, only backs up ~/.hermes/) |
| `~/.hermes/scripts/cleanup_backups.py` | Retention cleanup (24h kept / 1-7d daily / 7d+ deleted) |
| `~/.hermes/scripts/restore.sh` | One-click restore from local/baidu/url |
| `~/.hermes/scripts/RESTORE_GUIDE.md` | Full recovery guide for Keke |
| `~/.hermes/backups/` | Backup destination (~107MB per full backup) |

## Monthly VPS Swap Note

When the US proxy VPS is swapped monthly:
- **I don't need reinstalling** — my body is on the permanent domestic server
- Only the proxy IP/tunnel needs updating for overseas access
- Baidu/GitHub backup targets stay the same