# 自动配置覆盖追踪指南

*来源：用户分享的社区最佳实践，2026-05-15*

## 第一步：现场取证，当前是谁写了什么？

1. **查看文件修改时间**：用 `ls -lh --full-time ~/.hermes/.env` 查看精确的修改时间
2. **追踪进程写入**：使用 `auditd` 审计 `.env` 文件的写操作，能精准抓到是哪个进程干的
3. **检查 inotify 等待**：临时执行 `while inotifywait ~/.hermes/.env; do echo "$(date): 文件被修改" >> ~/env_changes.log; cat ~/.hermes/.env >> ~/env_changes.log; done`（需安装 inotify-tools）

## 第二步：逐个排查"嫌疑人"

### 嫌疑人一：自动配置工具（如 Cordon）
Cordon 在执行 `cordon setup hermes` 时，会自动重写 `~/.hermes/.env` 注入代理和 CA 证书。检查是否运行过 `cordon service install` 或 `cordon start`，以及 `~/.hermes/.env.cordon.bak` 备份文件。

### 嫌疑人二：系统服务管理器（systemd）
systemd 服务文件中的 `ExecStartPre`、`EnvironmentFile` 等配置可能修改配置。查看 `sudo systemctl cat hermes-gateway` 和 `sudo systemctl list-timers`。

### 嫌疑人三：定时任务（Cron Jobs）
定时脚本可能执行了配置恢复或备份还原操作。检查 `crontab -l`、`sudo crontab -l` 及 `/etc/cron.d/` 等目录。

### 嫌疑人四：终端配置文件（Shell RC）
启动新终端时自动设置的代理变量可能错误地被写入了文件。查看 `~/.bashrc`、`~/.zshrc`、`~/.profile` 中是否包含写 `.env` 的逻辑。

## 第三步：如果抓到真凶

| 真凶 | 处置方法 |
|------|---------|
| **Cordon** | 运行 `cordon disable hermes` 撤销集成，或用 `cordon env --scope user` 导出变量手动管理 |
| **systemd** | 执行 `sudo systemctl edit hermes-gateway --full` 编辑服务文件并移除异常配置，然后 `sudo systemctl daemon-reload && sudo systemctl restart hermes-gateway` |
| **Cron/脚本** | 注释或删除相应定时任务即可 |
