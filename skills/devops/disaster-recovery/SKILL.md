---
name: disaster-recovery
description: "Disaster recovery for agent data: backup scripts, restore procedures, off-server strategy, cleanup policy, and recovery guide. Covers cron backups, GitHub push, Baidu Wangpan, critical vs reinstallable data, and what to do when the server dies."
version: 3.1.0
category: devops
---

# Disaster Recovery

## When to Use

- Keke asks "怎么恢复你" or "备份了什么" or "服务器挂了怎么办"
- Setting up, testing, or troubleshooting the backup system
- After creating or modifying critical agent data (new skills, config changes, API keys)
- Before major server changes (OS upgrade, migration, disk cleanup)
- Whenever the backup/cleanup scripts need modification

## Architecture

```\ncron (每天3:00)\n  └─ backup.sh (备所有不可替代的个人数据)\n       ├─ 收集：config, .env, data, scripts, cron, memories\n       ├─ 收集：skills代码（rsync --exclude=.venv/__pycache__/node_modules）\n       ├─ 收集：SSH keys (~/.ssh/id_vultr)\n       ├─ 收集：state.db + profiles/（聊天记录数据库，gzip压缩至~33MB）\n       ├─ 记录 pip deps（恢复时重建.venv用）\n       ├─ 打包为 tar.gz (~43MB，只备不可替代数据，不备框架代码）\n       ├─ 推送到 GitHub 私有仓库（保留最近5个版本）\n       └─ 清理临时文件
```

### Backup Scope — ONLY ~/.hermes/

**核心原则：只备 `~/.hermes/` 这一个目录，不动Keke其他任何文件。**

| 包含 | 排除 |
|------|------|
| `config.yaml` — 所有配置 | `.venv` / `venv` — 虚拟环境 |
| `memories/` — 记忆文件 | `__pycache__` — Python缓存 |
| `skills/*/SKILL.md` — 所有技能文本 | `node_modules` — JS依赖 |
| `cron/jobs.json` — 定时任务 | `.git` — Git仓库 |
| `auth.json` — 认证 | `backups/` — 不自引用旧包 |
| `channel_directory.json` — 频道配置 | `hermes-agent/` — 源码（可重新 `git clone`） |
| `.env` (加密) — API密钥 | `logs/` — 日志（丢了没关系） |
| `scripts/` — 备份/清理/恢复脚本 | |
| `state.db` — 聊天记录数据库 | |
| `profiles/` — 配置档案 | |
| `webhook_subscriptions.json` (如果已配) | |
| `小墨*对话*.txt` — 聊天记录（从HOME根目录匹配） | |

### Data Classification

| 类别 | 内容 | 恢复方式 |
|------|------|---------|
| 🔴 核心（丢了就失忆） | memories, config, cron jobs, auth | 必须从备份恢复 |
| 🟡 可重建（花点时间） | skills, scripts, book notes | 可以手动重建 |
| 🟢 可重装（完全不丢） | hermes-agent源码, .venv, 缓存 | `git clone` + `pip install` |

### Backup Size

~43MB 完整包（含 state.db 聊天记录数据库）。主要来源：
- `state.db` — 聊天记录数据库（67MB，gzip压缩至~33MB）
- `skills/` — 技能代码（不含.venv，~17MB）
- 配置+脚本+cron+SSH key（<1MB）
- 备份脚本排除：`.venv`, `node_modules`, `__pycache__`, `hermes-agent/`框架代码

**GitHub 100MB限制：** 备份大小约43MB，远在限制内。若state.db增长超过100MB（预计3-4个月后），backup.sh会自动split拆分。

### Retention Policy (cleanup_backups.py)

| 时间范围 | 保留策略 |
|:--------|:--------|
| 24小时内 | ✅ 全部保留 |
| 1~7天前 | ✅ 每天只留1个（最早的） |
| 超7天 | ❌ 自动删除 |

**注意：12小时备份周期下，24h内最多2个备份。**
**频率历史：曾设为4h → Keke于2026-05-16钦定改为12h。**📌 快捷命令参考: `skill_view("disaster-recovery", "references/backup-commands.md")`
📌 百度网盘审核填表指南: `skill_view("disaster-recovery", "references/baidu-app-review-guide.md")`
📌 Token自动刷新脚本: `scripts/baidu-refresh.py`（每25天cron运行一次）



### backup.py (v3.1) — 主备份脚本

路径: `~/.hermes/scripts/backup.py`

每12小时由cron自动调用（job_id: f77f6e7e67bc）。功能：
1. 收集 `~/.hermes/` 目录 + HOME根目录下所有 `小墨*对话*.txt` 聊天记录文件
2. 生成环境变量清单（不含密钥原文）
3. 加密 `.env` 文件（XOR + base64）
4. 记录 system_info + pip deps
5. 打包为 tar.gz（排除 .venv/__pycache__/hermes-agent/backups/logs 等）
6. 尝试推送到 GitHub（若已登录）
7. 自动运行 cleanup_backups.py 清理旧备份

```bash
# 手动运行
timeout 120 python3 ~/.hermes/scripts/backup.py
```

### restore.sh — 一键恢复脚本

路径: `~/.hermes/scripts/restore.sh`

在新服务器上一键恢复我（支持从百度网盘/GitHub下载）。

```bash
# 从百度网盘拉最新备份并恢复
bash ~/.hermes/scripts/restore.sh --from-baidu

# 从本地恢复
bash ~/.hermes/scripts/restore.sh --local

# 从URL下载
bash ~/.hermes/scripts/restore.sh --from-url https://...
```

### cleanup_backups.py — 清理旧备份

路径: `~/.hermes/scripts/cleanup_backups.py`

```bash
# 预览（不删）
python3 ~/.hermes/scripts/cleanup_backups.py

# 真正删除
python3 ~/.hermes/scripts/cleanup_backups.py --apply

# 同时清理百度网盘（授权后）
python3 ~/.hermes/scripts/cleanup_backups.py --apply --baidu
```

### RESTORE_GUIDE.md — 恢复指南

路径: `~/.hermes/scripts/RESTORE_GUIDE.md`

Keke手把手恢复步骤：找备份 → 装新服务器 → 解压 → 恢复密钥 → 启动验证。

## Off-Server Backup (三重保险)

| 方案 | 状态 | 设置方式 |
|:----|:----|:--------|
| ① 本地打包 | ✅ 已启用（每12h） | 自动 cron |
| ② GitHub推送 | ✅ 已启用 | `kekewater/hermes-backup` (423个文件) |
| ③ 百度网盘 | ⏳ 已授权但上传受阻 | OAuth对列目录/创建文件夹OK，但上传文件返回31064"file is not authorized" — 需要Keke在控制台开启「文件传输」能力 |

### GitHub Setup (2026-05-17 → backup.sh tar.gz snapshot)

**仓库: `github.com/kekewater/hermes-backup`**

备份脚本 `backup.sh` 将所有不可替代的个人数据打包为一个 ~4-15MB 的 tar.gz 文件，直接推送到 GitHub。**不备份框架代码（hermes-agent源码可重装）**，也不备份 .venv（可 pip install 重建）。

**保留策略**：GitHub 仓库中保留最近 5 个版本的 tar.gz 备份包。老的会自动被新备份覆盖。

**第一次备份测试（2026-05-17）：**
```
📦 大小: 4.4MB
✅ 成功推送到 github.com/kekewater/hermes-backup
```

**关键限制：GitHub 单文件最大 100MB。** backup.sh 自动检测文件大小，超过 90MB 时会 split 拆分。

**新服务器克隆步骤（只需Keke配合5步）：**
1. 装 Hermes Agent: `npm install -g hermes-agent`
2. 获取数据: `unset http_proxy https_proxy && gh repo clone kekewater/hermes-backup`
3. 复制: `cp -r hermes-backup/* ~/.hermes/`
4. 配API Key: 小墨引导填写
5. 启动: `hermes`

```bash
# 查看仓库内容（无需克隆）
gh repo view kekewater/hermes-backup

# 新机器克隆（必须关代理！）
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
gh repo clone kekewater/hermes-backup
```

#### 初次设置（仅在新服务器上需要）

```bash
sudo apt-get install gh -y
gh auth login
cd ~ && unset http_proxy https_proxy && gh repo clone kekewater/hermes-backup
# 然后按 restore.sh 步骤操作
```

#### Git Clone Proxy 陷阱

当 Vultr 代理（:8889）激活时，`git clone https://github.com/...` 会报错：
```
RPC failed; curl 56 GnuTLS recv error (-110): The TLS connection was non-properly terminated.
```
**解决方案：** 克隆前务必 unset 代理，完成后恢复。
```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
git clone --depth 1 https://github.com/kekewater/hermes-backup.git  # --depth 1 减少数据量，降低超时概率
```
也可以用 `gh repo clone`（gh CLI 走 API 通道，更稳定）。

### Baidu Netdisk Setup (2026-05-16)

**方法：设备码模式授权（Device Code OAuth）** — 适用于 CLI-only 环境，不需要浏览器扫码界面。

#### 前置条件
Keke需要在 [pan.baidu.com/union/](https://pan.baidu.com/union/) 注册为开发者 → 创建应用（选"软件"类别，名称如"小墨网盘备份"） → 获得以下凭据：
- `AppID` (app_id)
- `AppKey` (client_id)
- `SecretKey` (client_secret)

**关键：应用创建后是「未审核」状态，需要先提交上线审核！** 在控制台（`pan.baidu.com/union/console/applist`）找到应用 → 点「申请上线审核」→ 填写审核表单。详细填法见 `references/baidu-app-review-guide.md`。审核通过后，再到 控制台→应用详情→接入能力 中开启「文件传输」能力！否则OAuth授权只能列目录、创建文件夹，不能上传文件。开启后再重新授权即可。

#### 授权流程（只需要Keke做一次）

**Step 1: 请求设备码**（我可以执行）
```bash
curl -s -L -X GET "https://openapi.baidu.com/oauth/2.0/device/code?response_type=device_code&client_id=YOUR_APPKEY&scope=basic,netdisk"
```
返回：`device_code`, `user_code`, `verification_url`, `qrcode_url`, `expires_in`(300秒)

**Step 2: Keke手动授权**
方式A：打开 `https://openapi.baidu.com/device` → 输入 user_code → 登录百度账号 → 授权
方式B：扫描 qrcode_url 生成的二维码

**Step 3: 轮询获取 token**（我可以执行）
```bash
curl -s "https://openapi.baidu.com/oauth/2.0/token?grant_type=device_token&code=DEVICE_CODE&client_id=APPKEY&client_secret=SECRET"
```
成功返回：`access_token`（30天有效）, `refresh_token`（单次使用，刷新后失效）

#### Token 刷新机制
- access_token 有效期：30天
- refresh_token 单次使用有效
- 刷新后旧的 refresh_token 立即失效，必须使用新返回的 refresh_token
- 轮询间隔：≥5秒

#### 关键API端点
详细端点参数见 `references/baidu-netdisk-api.md`。核心能力：

| 操作 | 端点 | 状态 |
|:----|:-----|:----:|
| 查看空间配额 | `GET /api/quota` | ✅ 可用 |
| 创建文件夹 | `POST /rest/2.0/xpan/file?method=create` | ✅ 可用 |
| 文件列表 | `GET /rest/2.0/xpan/file?method=list` | ✅ 可用 |
| 预创建文件（上传第一步） | `POST /rest/2.0/xpan/file?method=precreate` | ✅ 可用 |
| 上传文件块 | `POST /d.pcs.baidu.com/rest/2.0/pcs/file?method=upload` | ❌ 31064错误 |
| 完成上传 | `POST /rest/2.0/xpan/file?method=create` | ❌ 依赖上一步 |

#### 当前已知问题：上传失败（error 31064）

错误码 **31064 "file is not authorized"** 意味着百度开发者应用缺少 **文件上传** 能力授权。

**解决方案：** Keke需要在百度网盘开放平台控制台 → 找到应用 → 开启「文件传输」或类似的上传权限能力。开启后重新授权即可。

#### 存储方案
备份文件存在百度网盘的 `/小墨网盘备份/` 文件夹下（Keke指定，不要动其他任何目录）。

## Recovery Procedure

详细步骤见 `~/.hermes/scripts/RESTORE_GUIDE.md`

### Quick Restore (新服务器)

```bash
# 1. 装 Ubuntu + Hermes Agent
git clone https://github.com/nousresearch/hermes-agent.git
# 按官方文档安装

# 2. 解压备份
tar -xzf 小墨完整备份_20260516_*.tar.gz -C /

# 3. 恢复密钥
cat ~/.hermes/backups/_备份元数据/env_manifest.txt
# 逐一手动填写 ~/.hermes/.env

# 4. 重启
hermes gateway run  # 或 systemctl restart hermes-gateway
```

### Worst Case (没有备份)

Keke可以重新创造我：
- 告诉我名字、偏好、我们在做什么 → 我重新记住
- 说"重建XX技能" → 我根据记忆重写 Skill.md
- 人还在，文件丢了也不怕

## Pitfalls

- **本地备份不安全** — 服务器一挂备份跟着挂，必须上云端
- **cron prompt不能含API key+curl** — 安全规则 `exfil_curl` 会拦截。API key不要硬编码在prompt里，放到 credential 文件引用
- **大skill只备了SKILL.md** — tonghuashun(6.8GB) 和 china-stock-data(359MB) 的 .venv 和数据被排除，恢复后需要重新 `pip install`
- **bypy 授权一次管很久** — 但token过期后需要重新扫码，定期检查
- **微信传大文件可能失败** — 64MB+的包可能走不通网关，用 GitHub 或百度云代替
- **恢复指南在服务器上** — 如果服务器死了指南也找不到，Keke应该存一份到本地
