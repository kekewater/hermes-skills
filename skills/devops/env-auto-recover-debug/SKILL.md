---
name: env-auto-recover-debug
description: 排查 .env 文件被自动恢复/覆盖的根因——按"现场取证→嫌疑人排查→根因处置"三部曲
version: 1.0.0
---

# .env 自动恢复排查指南

## 触发场景

`~/.hermes/.env` 文件中的配置行（尤其是代理设置如 `HTTP_PROXY`/`socks5://`）被反复写回，即使手动删除后仍会恢复。

> **典型现象：** 微信等直连HTTP服务发送失败（`Expected HTTP/, RTSP/ or ICE/: b'\\x05\\xff'`）——说明 SOCKS5 协议抢占连接。

---

## 第一步：现场取证

### 1.1 查看文件修改时间

```bash
ls -lh --full-time ~/.hermes/.env
```

### 1.2 查看 .env 当前实际生效的配置（忽略注释行）

```bash
grep -v '^\s*#' ~/.hermes/.env | grep -v '^\s*$'
```

### 1.3 安装 auditd 审计写入操作（精准抓凶手）

```bash
sudo apt install auditd -y
sudo auditctl -w /home/ubuntu/.hermes/.env -p wa -k hermes_env_change
```

### 1.4 查看审计日志

```bash
# 查今天的
sudo ausearch -k hermes_env_change --start today

# 查看活跃规则
sudo auditctl -l
```

### 1.5 Inotify 实时监控（临时，适合测试时盯）

```bash
# 需要安装 inotify-tools
while inotifywait ~/.hermes/.env; do
  echo "$(date): 文件被修改" >> ~/env_changes.log
  cat ~/.hermes/.env >> ~/env_changes.log
done
```

---

## 第二步：逐个排查"嫌疑人"

### 嫌疑人一：Cordon（自动配置工具）

```bash
which cordon && cordon --version || echo "未安装"
ls -la ~/.hermes/.env.cordon.bak 2>/dev/null
```

Cordon 执行 `cordon setup hermes` 时会自动重写 `.env` 注入代理和CA证书。

**处理：**
```bash
cordon disable hermes            # 撤销集成
cordon env --scope user           # 导出变量手动管理
```

### 嫌疑人二：systemd 服务

```bash
sudo systemctl cat hermes-gateway 2>/dev/null    # 查看服务文件
sudo systemctl list-timers --no-pager | head -20 # 查看定时器
```

检查 `ExecStartPre`、`EnvironmentFile` 等配置。

**处理：**
```bash
sudo systemctl edit hermes-gateway --full        # 编辑服务文件
sudo systemctl daemon-reload && sudo systemctl restart hermes-gateway
```

### 嫌疑人三：定时任务（Cron Jobs）

```bash
crontab -l                     # 用户 cron
sudo crontab -l                # 系统 cron
ls -la /etc/cron.d/            # cron.d 目录
```

### 嫌疑人四：终端配置文件（Shell RC）

```bash
grep -n '\.env' ~/.bashrc ~/.zshrc ~/.profile ~/.bash_profile 2>/dev/null
grep -rn 'socks5\|HTTP_PROXY\|HTTPS_PROXY\|PROXY' ~/.bashrc ~/.zshrc ~/.profile 2>/dev/null
```

### 嫌疑人五：Hermes 自身 env_loader

检查 `~/.hermes/hermes-agent/hermes_cli/env_loader.py`：
- `_sanitize_env_file_if_needed()` 会读取并重写 .env（但只修复损坏行，不会添加）
- `load_hermes_dotenv()` 每次 gateway/CLI 启动时都会读取

### 嫌疑人六：Gateway 重启/热更逻辑

检查 gateway 启动命令：
```bash
ps aux | grep hermes
# 常见: python -m hermes_cli.main gateway run --replace
```

`--replace` 参数可能触发配置重载。

---

## 第三步：抓根因 & 处置

| 元凶 | 典型症状 | 处理方案 |
|------|---------|---------|
| Cordon | .env 有 `.cordon.bak` 备份 | `cordon disable hermes` |
| systemd | 有 `hermes-gateway.service` | 编辑服务文件移除异常配置 |
| Cron | crontab 有写 `env` 的任务 | 注释/删除定时任务 |
| Shell RC | bashrc/zshrc 有写 `.env` 的逻辑 | 删除对应行 |
| Gateway 热更 | 重启后 .env 恢复 | 避免在 .env 放代理，改放 config.yaml |

### 根治建议

如果确认代理设置不需要全局生效（只有特定场景需要），**不要在 .env 写 `HTTP_PROXY`/`HTTPS_PROXY`/`ALL_PROXY`**，改为：

- **按需设置**：只在启动脚本中 export（如 start_vultr_proxy.sh）
- **config.yaml**：在 hermes 的 provider/base_url 层面处理
- **工具层面**：只在特定工具调用时通过 `env=` 参数传入

---

## 验证 & 确认

```bash
# 确认当前 .env 干净
grep -v '^\s*#' ~/.hermes/.env | grep -v '^\s*$'

# 重启 gateway 检查是否恢复
hermes restart
grep -i 'proxy\|socks' ~/.hermes/.env

# 查看 auditd 日志确认没有新写入
sudo ausearch -k hermes_env_change --start today
```
