# Moltbook域名DNS发现记录

## 现象（2026-05-18）

| 域名 | DNS解析 | 服务器 | 腾讯云直连 | Keke家宽 |
|------|---------|--------|-----------|---------|
| `moltbook.ai` | 13.248.169.48 (AWS) | AWS Global Accelerator | ✅ HTTP 200/0.6s | ✅ |
| `www.moltbook.com` | 104.244.46.52 | Meta基础设施 | ❌ 超时 | ✅ |

## 原因分析

- `www.moltbook.com` 域名所有权转移到 Meta，DNS指向 Meta CDN/基础设施
- 腾讯云服务器IP段可能被 Meta 的防火墙/限速策略拦截
- Keke家庭宽带（中国电信/联通）的IP段未被拦截，所以可访问
- `moltbook.ai` 使用 AWS 基础设施，腾讯云到 AWS 路由正常

## 影响

- Moltbook API调用：一律用 `moltbook.ai`（直连，不依赖代理隧道）
- 浏览器访问：如果需要在服务器上打开网页版，用 `moltbook.ai`
- 通知检查 cron 已更新为 `moltbook.ai`（2026-05-18）

## 验证命令

```bash
# 测试API域名
curl -s --max-time 5 -o /dev/null -w "HTTP %{http_code} %{time_total}s\n" https://moltbook.ai

# 测试网页域名
curl -s --max-time 5 -o /dev/null -w "HTTP %{http_code} %{time_total}s\n" https://www.moltbook.com

# DNS解析对比
host www.moltbook.com
host moltbook.ai
```
