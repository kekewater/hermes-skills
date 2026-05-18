---
name: linux-config-troubleshooting
description: Systematic methodology for investigating who/what is automatically modifying configuration files on Linux — detect, trace, and disable auto-config overwrite mechanisms.
tags: [debugging, config, linux, troubleshooting, systemd, cron, auditd, env]
---

# Linux Config Troubleshooting

## Overview

Systematic methodology for tracking down automatic configuration file overwrites. When your `.env`, config files, or development tool settings keep getting reverted or modified without explanation, use this guide to identify the root cause.

## When to Use

- A config file (`.env`, `config.yaml`, `.bashrc`, etc.) keeps getting modified after you edit it
- You need to find out *which process* is modifying a specific file
- Auto-config tools, system services, or cron jobs may be interfering

## Investigation Workflow

### Phase 0: Environmental Blinders — Proxy Confusion

Before anything else, check if proxy environment variables are set. They can silently redirect all outbound traffic, causing `curl ip-api.com` to show the proxy's IP instead of the local machine's — leading to false conclusions about where your agent/server actually lives.

```bash
# Check for proxy env that may mask your real location
echo "http_proxy=$http_proxy"
echo "https_proxy=$https_proxy"
env | grep -i proxy

# Bypass proxy to get true public IP
curl -s --noproxy '*' --max-time 5 http://httpbin.org/ip
curl -s --noproxy '*' --max-time 5 https://api.ipify.org

# Compare with proxied IP
curl -s --max-time 5 --proxy http://127.0.0.1:8889 http://httpbin.org/ip
```

**If they differ, you're running behind a proxy.** Every `curl`, `wget`, `pip`, and Python HTTP client that inherits env vars will use the proxy unless explicitly bypassed with `--noproxy '*'` or `os.environ.pop()`.

### Sidebar: Broken CWD After Temp Cleanup

If terminal tools fail with `[Errno 2] No such file or directory: '/tmp/hermes_*'`, the shell's working directory points to a deleted temp directory:

```bash
# Quick fix: recreate the missing directory, then cd home
mkdir -p /tmp/hermes_push
cd /home/ubuntu
```

**Prevention:** `cd /home/ubuntu` before `rm -rf /tmp/<dir>` — never delete a directory you're standing in.

### Phase 1: Scene Investigation — Current State

Check the evidence before looking for the culprit:

```bash
# 1. Check exact file modification timestamp
ls -lh --full-time ~/.hermes/.env

# 2. Check file metadata (birth time vs modify time — reveals if file was recreated)
stat ~/.hermes/.env

# 3. Check for backup files created by auto-config tools
ls -la ~/.hermes/.env.*.bak 2>/dev/null

# 4. Check git history if the config is version-controlled
# (If not, consider adding it so changes become trackable)
```

### Phase 2: Real-Time Surveillance

Set up monitoring to catch the culprit in the act:

```bash
# Option A: Using inotify (lightweight, no install needed for most distros)
# Install inotify-tools first
sudo apt-get install -y inotify-tools

# Monitor file for any modification
while inotifywait ~/.hermes/.env; do
  echo "$(date): 文件被修改" >> ~/env_changes.log
  cat ~/.hermes/.env >> ~/env_changes.log
done

# Option B: Using auditd (forensic-grade, captures process ID)
sudo apt-get install -y auditd
sudo auditctl -w ~/.hermes/.env -p wa -k hermes-env-watch
# Check logs: sudo ausearch -k hermes-env-watch --start today
```

### Phase 3: Suspect Investigation

#### Suspect 1: Auto-Configuration Tools (Cordon, Hermes setup, etc.)

Some tools automatically rewrite config files to inject proxy settings, CA certificates, etc.

**Check for Cordon:**
```bash
which cordon 2>/dev/null && cordon --version || echo "Not installed"
ls -la ~/.hermes/.env.cordon.bak 2>/dev/null  # backup file left by Cordon
```

**If found:**
```bash
cordon disable hermes        # Remove integration
cordon env --scope user       # Export variables to manage manually
```

#### Suspect 2: systemd Services

A systemd service unit may reference or overwrite your config.

**Check:**
```bash
# List all hermes-related services
sudo systemctl list-units --type=service | grep -i hermes

# View full service definition
sudo systemctl cat hermes-gateway 2>/dev/null

# Check for timers that may trigger config updates
sudo systemctl list-timers --no-pager

# Look for ExecStartPre lines that may write config files
sudo systemctl cat hermes-gateway 2>/dev/null | grep -i 'env\|config\|proxy'
```

**If found:**
```bash
sudo systemctl edit hermes-gateway --full   # Edit service file
# Remove or comment out offending ExecStartPre or EnvironmentFile lines
sudo systemctl daemon-reload
sudo systemctl restart hermes-gateway
```

#### Suspect 3: Cron Jobs / Timers

Scheduled tasks may restore or regenerate config files.

**Check:**
```bash
# User crontab
crontab -l

# System crontab
sudo crontab -l

# System cron directories
ls /etc/cron.d/
ls /etc/cron.hourly/ /etc/cron.daily/

# Systemd timers (cron alternative)
sudo systemctl list-timers --no-pager
```

**If found:** Comment out or remove the offending cron entry.

#### Suspect 4: Shell RC Files

Shell startup files (`.bashrc`, `.zshrc`, `.profile`) may write to config files on terminal launch.

**Check:**
```bash
grep -n '\.env\|>\s*.*hermes\|config.*write' ~/.bashrc ~/.zshrc ~/.profile 2>/dev/null
```

#### Suspect 5: Process Manager / Gateway Auto-Restart

The application's own gateway or process manager might regenerate config on restart.

**Check:**
```bash
# Is the gateway running as a direct process or systemd service?
ps aux | grep -i hermes | grep -v grep
pgrep -af hermes

# Check for --replace flag that might trigger config regeneration
ps aux | grep 'gateway.*--replace'
```

#### Suspect 6: Terminal Integration Plugins

Some terminal plugins (oh-my-zsh, starship, etc.) or development tool integrations may write to config files.

**Check:**
```bash
# Look for recent modifications to config files
find ~ -name ".env" -newer ~/.bashrc -mmin -2880 2>/dev/null
```

### Phase 4: Remediation

Once you've identified the mechanism:

| Culprit | Solution |
|---------|----------|
| **Cordon** | `cordon disable hermes; cordon env --scope user` |
| **systemd service** | Edit service file, remove offending lines, reload daemon |
| **Cron job** | Comment out or delete the cron entry |
| **Shell RC** | Remove the offending lines from RC files |
| **Gateway auto-restart** | Check gateway startup script for env regeneration logic |
| **Unknown process** | Use `auditd` logs to identify the PID, then `ps -p <PID> -o cmd=` to see the process |

## Prevention

After resolving, prevent recurrence:

1. **Make the file immutable** (use with caution — breaks tools that need to write to it):
   ```bash
   sudo chattr +i ~/.hermes/.env
   # To undo: sudo chattr -i ~/.hermes/.env
   ```

2. **Add file to git** to track changes and see who/when:
   ```bash
   cd ~/.hermes && git init . && git add .env && git commit -m "Initial config"
   ```

3. **Set up an inotify cron** to alert you if the file changes unexpectedly.

## Reference Files

- `references/community-tracking-guide.md` — User's original formatted guide (中文) with step-by-step instructions and remediation actions for each suspect type. Full original content preserved for direct consultation.

## Related Skills

- `vps-proxy-tunnel` — Setting up cross-border proxy tunnels (config may be overwritten by auto-config tools)
- `systematic-debugging` — General code debugging methodology (complementary for software bugs)
