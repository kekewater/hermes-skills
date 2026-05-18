# Baidu Netdisk API Reference (2026-05-16)

## Overview
We use Baidu Netdisk (百度网盘) as one of three backup destinations. The OAuth flow uses **device code mode** (设备码模式), which is headless-friendly (no browser required for the agent — Keke only needs to scan once).

## OAuth Flow

### 1. Device Code Request
```bash
curl -s -L -X GET "https://openapi.baidu.com/oauth/2.0/device/code?response_type=device_code&client_id=$CLIENT_ID&scope=basic,netdisk"
```
Response:
```json
{
  "device_code": "48...c",
  "user_code": "av5ptmsd",
  "verification_url": "https://openapi.baidu.com/device",
  "qrcode_url": "https://openapi.baidu.com/device/qrcode/.../av5ptmsd",
  "expires_in": 300,
  "interval": 5
}
```
- `expires_in=300` — 5分钟内必须完成授权
- `interval=5` — 轮询间隔至少5秒

### 2. User Authorization
Keke opens `https://openapi.baidu.com/device` → enters `user_code` → logs in → authorizes.

### 3. Token Polling
```bash
curl -s "https://openapi.baidu.com/oauth/2.0/token?grant_type=device_token&code=$DEVICE_CODE&client_id=$CLIENT_ID&client_secret=$CLIENT_SECRET"
```
Success response:
```json
{
  "access_token": "126.xxxxx.yyyyy",
  "refresh_token": "127.xxxxx.zzzzz",
  "expires_in": 2592000,
  "scope": "basic netdisk"
}
```

Polling errors:
- `"authorization_pending"` → user hasn't authorized yet, retry in `interval` seconds
- `"slow_down"` → polling too fast, increase interval to 10s
- `"expired_token"` → device_code expired, restart from step 1

## Token Refresh

access_token expires in 30 days. Refresh mechanism:
```bash
curl -s "https://openapi.baidu.com/oauth/2.0/token?grant_type=refresh_token&refresh_token=$REFRESH_TOKEN&client_id=$CLIENT_ID&client_secret=$CLIENT_SECRET"
```
**Important:** refresh_token is single-use — the response contains a new one. Always save the new refresh_token.

## API Endpoints

All endpoints require `access_token` as query parameter and `User-Agent: xiao-mo-keke/1.0` header.

### GET /api/quota — Storage Quota
```bash
curl -s "https://pan.baidu.com/api/quota?access_token=$TOKEN"
```
Response:
```json
{"used": 1949910425600, "total": 17592186044416}
```
- `used` in bytes (1.95TB)
- `total` in bytes (16TB)

### POST /rest/2.0/xpan/file?method=create — Create Folder
```bash
curl -s -X POST "https://pan.baidu.com/rest/2.0/xpan/file?method=create&access_token=$TOKEN" \
  -d "path=/小墨网盘备份&size=0&isdir=1&rtype=1"
```
- `path`: 文件夹路径（UTF-8 URL编码）
- `isdir=1`: 创建的是目录
- `rtype=1`: 自动重命名（如果已存在）

### GET /rest/2.0/xpan/file?method=list — List Files
```bash
curl -s "https://pan.baidu.com/rest/2.0/xpan/file?access_token=$TOKEN&method=list&dir=/小墨网盘备份&order=time&desc=1"
```
Response fields:
- `errno`: 0 = success
- `list[].server_filename`: 文件名
- `list[].size`: 文件大小（字节）
- `list[].isdir`: 是否是目录
- `list[].path`: 完整路径
- `list[].fs_id`: 文件系统ID

### POST /rest/2.0/xpan/file?method=precreate — Prepare Upload (Step 1)
```bash
curl -s -X POST "https://pan.baidu.com/rest/2.0/xpan/file?method=precreate&access_token=$TOKEN" \
  -d "path=/小墨网盘备份/filename.txt&size=13&isdir=0&rtype=1&block_list=[\"md5hash\"]"
```
- `block_list`: JSON数组，每个元素是与对应文件块的MD5
- 返回 `uploadid` 用于后续上传步骤

### POST /d.pcs.baidu.com/rest/2.0/pcs/file?method=upload — Upload Data (Step 2)
```bash
curl -X POST "https://d.pcs.baidu.com/rest/2.0/pcs/file?method=upload&access_token=$TOKEN&path=/小墨网盘备份/filename.txt&uploadid=$UPLOADID&partseq=0" \
  -F "file=@localfile.txt"
```

### POST /rest/2.0/xpan/file?method=create — Finalize Upload (Step 3)
```bash
curl -s -X POST "https://pan.baidu.com/rest/2.0/xpan/file?method=create&access_token=$TOKEN" \
  -d "path=/小墨网盘备份/filename.txt&size=13&isdir=0&uploadid=$UPLOADID&block_list=[\"md5hash\"]"
```

## Known Errors & Troubleshooting

| Error Code | Message | Cause | Fix |
|:----------|:--------|:------|:----|
| 31064 | "file is not authorized" | App lacks file upload capability | Keke enables in console: 控制台 → 应用详情 → 接入能力 → 开启文件传输 |
| 31023 | "param error" | Wrong parameters for API call | Check required params for the method |
| errno=2 | "参数错误" | precreate failed | Check path format, block_list must be valid JSON array |
| errno=31500 | system error | Upload sequence incomplete | Complete all 3 steps (precreate→upload→create) |
| 403 (raw) | "file is not authorized" | Using PCS API without permission | Same as 31064 — capability not enabled |
| auth_pending | polling response | User hasn't scanned yet | Keep polling at `interval` seconds |
| slow_down | polling response | Polling too fast | Increase interval to 10s |
| expired_token | polling response | device_code expired (>5min) | Regenerate device_code |

## Credential Storage

Credentials stored in `~/.hermes/baidu_credentials.json`:
```json
{
  "access_token": "126.xxx",
  "refresh_token": "127.xxx",
  "expires_in": 2592000,
  "client_id": "GP7JpRmq5...",
  "client_secret": "sOKt8vxMr...",
  "app_id": "123328717"
}
```
Also added to `.env`:
- `BAIDU_APP_ID`
- `BAIDU_CLIENT_ID`
- `BAIDU_CLIENT_SECRET`

## Security Notes
- 只操作 `/小墨网盘备份/` 文件夹（Keke指定），不碰其他任何目录
- refresh_token 单次使用，每次刷新后必须保存新的
- device_code 5分钟过期，轮询超时后需重新生成
- User-Agent 必须设置（百度会拒绝默认python-requests标识）
