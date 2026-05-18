# iFinD Token 刷新工作流

## 背景

同花顺 iFinD API 使用双 Token 机制：
- **access_token** — 用于实际 API 调用，7天有效
- **refresh_token** — 用于换取新的 access_token，~44天有效

如果 refresh_token 也过期（错误码 -1301），无法在 Linux 端自助续期，必须从 Windows iFinD 客户端重新获取。

## 刷新命令

```bash
# 手动刷新（从 ifind_config.json 读取 refresh_token，换取新的 access_token + refresh_token）
python3 ~/.hermes/scripts/stock_api.py ifind-refresh

# 成功后验证
python3 ~/.hermes/scripts/stock_api.py ifind-quote 600519
```

## 自动刷新

Cron 配置（每周一、四 10:00，覆盖 7 天有效期）：
```
0 10 * * 1,4 cd ~/ && python3 ~/.hermes/scripts/stock_api.py ifind-refresh
```

## 关键陷阱

### 必须保存新 refresh_token
刷新接口不仅返回新的 access_token，也返回新的 refresh_token。脚本必须**同时保存两者**，不能只更新 access_token。

### token 存储文件
路径：`~/.hermes/data/ifind_config.json`

格式：
```json
{
  "access_token": "xxx",
  "refresh_token": "xxx",
  "access_expires": "2026-05-24 16:13:42",
  "refresh_expires": "2026-06-30 11:59:17"
}
```

### 写入文件可能被代理 env 干扰
环境变量 `http_proxy=http://127.0.0.1:8889` 会影响某些 Python 库的文件写入。如果 `ifind-config.json` 中 access_token 写入后为空：
1. 检查脚本是否在写入文件时也走了代理
2. 在文件写入前清除代理 env：`os.environ.pop(key, None)`

### 验证方法
```bash
python3 ~/.hermes/scripts/stock_api.py ifind-quote 600519
# 正确返回：贵州茅台 ¥1,342.17 PE 20.18 ...
# 错误返回：-1301（双过期，需找 Windows）
```

## 相关文件

| 文件 | 作用 |
|------|------|
| `~/.hermes/scripts/stock_api.py` | `ifind-refresh` 命令实现 |
| `~/.hermes/data/ifind_config.json` | Token 持久化存储 |
