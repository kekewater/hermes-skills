#!/bin/bash
# VPS Proxy Tunnel — 启动脚本
# 用法: bash templates/startup.sh
# 填入你的VPS信息后使用

VPS_IP="<YOUR_VPS_IP>"
LOCAL_PORT="8888"
SSH_KEY="$HOME/.ssh/id_ed25519"

echo "[1/3] 检查 VPS 代理服务..."
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
    -i "$SSH_KEY" root@${VPS_IP} \
    "pgrep -f 'proxy.*${LOCAL_PORT}' > /dev/null 2>&1 || (pip3 install -q proxy.py && nohup proxy --hostname 127.0.0.1 --port ${LOCAL_PORT} --log-level warning > /dev/null 2>&1 & sleep 2; echo 'proxy.py 已启动')"

echo "[2/3] 建立 SSH 隧道..."
pkill -f "ssh.*-L ${LOCAL_PORT}:127.0.0.1:${LOCAL_PORT}" 2>/dev/null
sleep 1

ssh -o StrictHostKeyChecking=no \
    -o ServerAliveInterval=30 \
    -o ServerAliveCountMax=3 \
    -i "$SSH_KEY" \
    -L ${LOCAL_PORT}:127.0.0.1:${LOCAL_PORT} -C -N -f \
    root@${VPS_IP}

if [ $? -eq 0 ]; then
    echo "✅ 代理隧道已建立 (127.0.0.1:${LOCAL_PORT})"
else
    echo "❌ 隧道建立失败"
    exit 1
fi

echo "[3/3] 验证连通性..."
curl -x http://127.0.0.1:${LOCAL_PORT} -s -o /dev/null -w "Google: %{http_code} (%{time_total}s)\n" https://www.google.com --max-time 10
curl -x http://127.0.0.1:${LOCAL_PORT} -s -o /dev/null -w "OpenRouter: %{http_code} (%{time_total}s)\n" https://openrouter.ai/api/v1/models --max-time 10

echo ""
echo "使用: curl -x http://127.0.0.1:${LOCAL_PORT} https://..."
