# Config File Auto-Recovery Investigation

**Scenario:** A config file (e.g. `~/.hermes/.env`, `~/.bashrc`, `~/.config/...`) keeps having certain lines restored after you manually removed them.

**Root pattern:** Something in the system lifecycle re-writes the file after each manual edit — a startup script, a daemon, a cron job, or a framework-level hook.

---

## The Four Suspects Framework

Systematically verify each suspect. No guessing.

### 1. ✅ Verify the Crime Scene

```bash
# Exact modification time (nanosecond precision)
ls -lh --full-time ~/.hermes/.env

# Current key-value pairs (skip comments)
grep -v '^\s*#' ~/.hermes/.env | grep -v '^\s*$'

# What changed versus a known-good backup (if any)
diff ~/.hermes/.env ~/.hermes/.env.bak
```

### 2. 🔍 Audit for Real-Time Traces

Install auditd for kernel-level file monitoring:

```bash
sudo apt install auditd -y
sudo auditctl -w /home/ubuntu/.hermes/.env -p wa -k hermes_env_change

# Review captured events
sudo ausearch -k hermes_env_change | tail -30
```

Or use inotify for lighter monitoring:

```bash
while inotifywait ~/.hermes/.env; do
  echo "$(date): 文件被修改" >> ~/env_changes.log
  cat ~/.hermes/.env >> ~/env_changes.log
done
```

### 3. 👮 Interrogate the Four Suspects

| # | Suspect | Check | Command |
|---|---------|-------|---------|
| 1 | **Cordon** (auto-config tool) | Does it exist? Any backup files? | `which cordon`; `ls ~/.hermes/.env.cordon.bak`; `cordon status` |
| 2 | **systemd** (service restores config) | Is hermes-gateway a service? Does ExecStartPre write .env? | `sudo systemctl cat hermes-gateway`; `sudo systemctl list-timers` |
| 3 | **Cron jobs** (scheduled restore) | User or system crons writing .env? | `crontab -l`; `sudo crontab -l`; `ls /etc/cron.d/`; `ls /etc/cron.hourly/` |
| 4 | **Shell RC** (login restores env) | bashrc/zshrc/profile writes to .env? | `grep -n '\.env\|PROXY\|socks\|export' ~/.bashrc ~/.zshrc ~/.profile` |

### 4. 🧠 Check Framework-Level Mechanisms

Beyond the four suspects, check:

- **Hermes env_loader** (`hermes_cli/env_loader.py`): This reads the .env on startup and can **sanitize** it (fix corrupted lines, remove stale `***` placeholders) — but it will NOT add new lines. It is innocent unless you're seeing lines being re-added.
- **Gateway restart scripts**: `~/.hermes/start_vultr_proxy.sh` or similar startup scripts may write proxy settings.
- **Hermes hooks**: `~/.hermes/hooks/` — any hooks that fire on gateway lifecycle events.

---

## Root Cause Resolution

Once identified:

| Culprit | Fix |
|---------|-----|
| Cordon | `cordon disable hermes` or use `cordon env --scope user` |
| systemd | `sudo systemctl edit hermes-gateway --full` → remove offending lines → `daemon-reload && restart` |
| Cron | Comment out or delete the cron job |
| Shell RC | Remove the write-to-.env logic from RC file |
| Startup script | Remove proxy-writing lines or use env vars instead of rewriting .env |
| Hermes hook | Remove or fix the hook script |

---

## Prevention

1. **Set up auditd** as above for future monitoring
2. **Keep a diff-safe backup** of a clean .env:
   ```bash
   cp ~/.hermes/.env ~/.hermes/.env.known-good
   ```
3. **Log gateway restarts** to correlate with file changes:
   ```bash
   sudo journalctl -u hermes-gateway --since "1 hour ago"
   ```
