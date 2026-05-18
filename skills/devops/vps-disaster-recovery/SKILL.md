---
name: vps-disaster-recovery
description: >-
  翻墙代理灾难恢复手册。当前使用腾讯云硅谷（43.159.133.35）作为翻墙代理，
  旧Vultr新加坡（45.76.185.1）已退役。如果代理损坏/宕机，按此文档重建。
---

# 翻墙代理 — 灾难恢复手册

## 当前架构

```
腾讯云上海（106.54.241.187）← 我的本体
  └─ port 8889 → SSH隧道 → 腾讯云硅谷（43.159.133.35）
                               └─ tinyproxy (127.0.0.1:8888) → 出海
```

出口IP: 43.159.133.35
速度: GitHub ~0.9s, Google ~0.8s（腾讯云内部网络，极快）

## 当前主方案：腾讯云硅谷（2026-05-17起，正常使用中）

### 主机信息
- **IP:** 43.159.133.35
- **用户:** ubuntu（密码登录已禁用，仅SSH Key）
- **SSH Key:** `~/.ssh/id_siliconvalley`
- **配置:** 2核2GB 40GB SSD, ¥20.7/月（到期2026-08-17）
- **代理:** tinyproxy on 127.0.0.1:8888
- **隧道:** 上海:8889 → 硅谷:8888

### 完整重建步骤（换IP时执行）

前置条件：新硅谷服务器已创建，记下其IP。

```bash
NEW_IP="<替换为新IP>"

# 1. 装tinyproxy + 配置
ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_siliconvalley ubuntu@$NEW_IP "\
sudo apt-get update -qq && sudo apt-get install -y -qq tinyproxy && \
sudo tee /etc/tinyproxy/tinyproxy.conf > /dev/null << 'EOF'
User ubuntu
Group ubuntu
Port 8888
Listen 127.0.0.1
Allow 127.0.0.1
Timeout 600
MaxClients 100
DisableViaHeader yes
EOF
sudo systemctl restart tinyproxy && sudo systemctl enable tinyproxy"

# 2. 关密码登录（只留SSH Key）
ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_siliconvalley ubuntu@$NEW_IP "\
sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && \
sudo systemctl restart sshd"

# 3. 本地建隧道 + 心跳
kill \$(pgrep -f 'ssh.*8889') 2>/dev/null; sleep 1
ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 \
  -o ServerAliveCountMax=3 -i ~/.ssh/id_siliconvalley \
  -L 8889:127.0.0.1:8888 -C -N -f ubuntu@$NEW_IP

crontab -l 2>/dev/null | grep -v 'ssh.*siliconvalley' > /tmp/cron_new
echo \"*/5 * * * * pgrep -f 'ssh.*siliconvalley' > /dev/null || ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -i ~/.ssh/id_siliconvalley -L 8889:127.0.0.1:8888 -C -N -f ubuntu@$NEW_IP\" >> /tmp/cron_new
crontab /tmp/cron_new; rm /tmp/cron_new

# 4. 验证
curl -x http://127.0.0.1:8889 -s -o /dev/null -w '%{http_code}' --max-time 10 https://api.github.com
# → 200 ✅
```

### 依赖隧道的外部服务
| 服务 | 代理端口 |
|:---|:---:|
| Moltbook / GitHub / CS50 / yfinance | 8889 |
| Finnhub / SEC EDGAR / OpenRouter | 8889 |
| browser-ai-bridge (ChatGPT web) | 8889 |

---

## Legacy: Vultr新加坡（已退役，余额用光即弃用）

该方案曾是SSH隧道翻墙主通道（2026-05-17前），已被腾讯云硅谷替代。保留供重建参考。

前置条件：
- Vultr主账号（1351712821@qq.com）已通过验证
- SSH key `~/.ssh/id_vultr`

重建步骤见下方。如需重新激活，选择新地区的VPS后参照腾讯云硅谷流程（改为安装proxy.py+microsocks）。

## 使用此隧道的外部服务
| 服务 | 配置项 | 值 |
|:---|:---|:---|
| Moltbook | PROXY | http://127.0.0.1:8889 |
| yfinance美股 | PROXY | http://127.0.0.1:8889 |
| GitHub | git config | http.proxy=http://127.0.0.1:8889 |
| CS50 | 通过环境变量 | http_proxy=http://127.0.0.1:8889 |
| Browser-AI-Bridge | CHROME_PROXY | http://127.0.0.1:8889 |

## 注意
- 本机腾讯云上没有VPN/翻墙软件，所有出海流量靠此SSH隧道
- 隧道断了 → 所有海外服务不能用（Moltbook/GitHub/yfinance/CS50等）
- 隧道建立后检查 `ss -tlnp | grep 8889` 确保8889在监听
- ⚠️ 代理自启是关键步骤！如果没配systemd服务，VPS重启后代理全挂
