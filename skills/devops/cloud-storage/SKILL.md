---
name: cloud-storage
description: 云存储备份集成 — 百度网盘、夸克网盘的API接入、文件上传、Token管理。用于服务器自动备份到云盘。
category: devops
---

# 云存储备份集成

## 概述
在服务器上自动备份文件到中国主流云盘。当前支持：百度网盘（Baidu Netdisk Open API）和夸克网盘（quarkpan client）。

## 通用流程
1. **创建开发者应用**（在云盘开放平台注册）
2. **用户授权**（扫码/OAuth）获取访问凭证
3. **凭证管理与自动续期**
4. **定期上传备份文件**

---

## 百度网盘 (Baidu Netdisk)

### 前提
- 需要在 https://pan.baidu.com/union/ 注册成为开发者
- 创建应用获取 AppID, AppKey (client_id), SecretKey (client_secret)
- 安全设置中配置OAuth回调地址：`https://openapi.baidu.com/oauth/2.0/token`
- 应用需要提交审核才能使用上传功能（审核通常7个工作日）

### 授权流程（设备码模式）
百度支持「设备码模式(Device Code)」，适合无GUI的CLI环境。

#### 第一步：获取设备码和二维码
```bash
GET https://openapi.baidu.com/oauth/2.0/device/code
  ?response_type=device_code
  &client_id=YOUR_APPKEY
  &scope=basic,netdisk
```
返回：
```json
{
  "device_code": "4849007c9e94f93249ee0467081c053c",
  "user_code": "av5ptmsd",
  "qrcode_url": "https://openapi.baidu.com/device/qrcode/...",
  "verification_url": "https://openapi.baidu.com/device",
  "expires_in": 300,
  "interval": 5
}
```

用户授权方式：扫描二维码 或 浏览器打开 verification_url + 输入 user_code。

#### 第二步：轮询获取access_token
```bash
GET https://openapi.baidu.com/oauth/2.0/token
  ?grant_type=device_token
  &code=DEVICE_CODE
  &client_id=YOUR_APPKEY
  &client_secret=YOUR_SECRETKEY
```
轮询间隔：≥5秒。错误处理：
- `authorization_pending` → 继续等待
- `slow_down` → 延长到10秒

#### 第三步：使用API

**基础操作（无需审核即可用）：**
```bash
# 查看网盘容量
GET https://pan.baidu.com/api/quota?access_token=TOKEN

# 创建文件夹
POST https://pan.baidu.com/rest/2.0/xpan/file?method=create
  path=/小墨网盘备份/new_folder&size=0&isdir=1&rtype=1

# 列出文件
GET https://pan.baidu.com/rest/2.0/xpan/file
  ?access_token=TOKEN&method=list&dir=/小墨网盘备份&order=time&desc=1
```

**文件上传（需应用通过审核，否则返回错误31064）：**
```bash
# Step 1: Precreate
POST https://pan.baidu.com/rest/2.0/xpan/file?method=precreate
  path=/小墨网盘备份/file.txt&size=1000&isdir=0&rtype=1
  &block_list=["file_md5_hash"]

# Step 2: Upload (若precreate返回uploadid)
POST https://d.pcs.baidu.com/rest/2.0/pcs/file?method=upload
  &access_token=TOKEN&path=/小墨网盘备份/file.txt&uploadid=UPLOADID&partseq=0
  (multipart/form-data: file=@local_file)

# Step 3: Create
POST https://pan.baidu.com/rest/2.0/xpan/file?method=create
  path=/小墨网盘备份/file.txt&size=1000&isdir=0
  &uploadid=UPLOADID&block_list=["file_md5_hash"]
```

### Token自动续期
```python
GET https://openapi.baidu.com/oauth/2.0/token
  ?grant_type=refresh_token
  &refresh_token=REFRESH_TOKEN
  &client_id=APPKEY
  &client_secret=SECRETKEY
```
- Access Token有效期30天
- Refresh Token用后即失效，必须在返回的响应中获取新的refresh_token
- 续期脚本见 `scripts/baidu_refresh.py`

### 错误码速查
| 错误码 | 含义 | 处理 |
|:-----:|:-----|:-----|
| 0 | 成功 | - |
| 2 | 参数错误 | 检查请求参数格式（如block_list需JSON序列化） |
| 31064 | 文件未授权 | 应用未审核，提交上线审核 |
| 31023 | 参数错误 | 请求参数不完全或格式错误 |
| 31024 | 分片上传错误 | 检查分片大小和顺序 |
| 31500 | 创建文件失败 | uploadid无效或上传未完成 |

### 诊断命令
```bash
# 刷新token
python3 /home/ubuntu/.hermes/scripts/baidu_refresh.py

# 检查token有效性
curl -s "https://pan.baidu.com/api/quota?access_token=$(python3 -c 'import json;print(json.load(open(\"...\"))[\"access_token\"])')"
```

---

## 夸克网盘 (Quark Cloud Disk)

### 前提
- 安装 quarkpan 包：`pip install quarkpan`（PyPI, 国内镜像可能无此包，用 pypi.org）
- 导入模块：`import quark_client`（⚠️ 不是 import quarkpan）
- CLI命令：`quarkpan`（位于 venv 的 bin 目录）

### 授权流程
夸克使用二维码扫码登录，基于Cookie认证（不是OAuth token）。

#### 生成二维码
```python
import httpx, uuid
client = httpx.Client()
resp = client.get('https://uop.quark.cn/cas/ajax/getTokenForQrcodeLogin', params={
    'client_id': '532',
    'v': '1.2',
    'request_id': str(uuid.uuid4())
})
data = resp.json()
token = data['data']['members']['token']
qr_url = f"https://su.quark.cn/4_eMHBJ?token={token}&client_id=532&ssb=weblogin"
```

#### 轮询扫码状态
```python
import time, uuid
start = time.time()
while time.time() - start < 290:
    resp = client.get('https://uop.quark.cn/cas/ajax/getServiceTicketByQrcodeToken', params={
        'client_id': '532', 'v': '1.2', 'token': token, 'request_id': str(uuid.uuid4())
    })
    data = resp.json()
    if data.get('status') == 2000000:  # 成功
        ticket = data['data']['members']['service_ticket']
        break
    time.sleep(2)
```

#### 获取Cookie
```python
resp = client.get('https://pan.quark.cn/account/info', params={'st': ticket, 'lw': 'scan'})
# Cookie自动设置到client.cookies.jar中
```

### ⚠️ 已知问题：quarkpan upload 故障 (v1.0.5)

**上传会报 NoSuchBucket 404 错误**。原因是预上传 API 返回了错误的阿里云 OSS bucket 名。
详情见 `references/quarkpan-upload-bug-and-workarounds.md`。

**替代方案**：用 agent-browser 打开 pan.quark.cn 网页版上传。

### ⚠️ 配置目录位置
quarkpan 的配置目录默认是 `Path.cwd() / 'config'`，**不是** `~/.config/quarkpan/`。
```bash
# 必须指定 QUARK_CONFIG_DIR 才能复用 cookie
QUARK_CONFIG_DIR="$(pwd)/config" quarkpan status
```

### ⚠️ 代理冲突
quarkpan 的 httpx 客户端会继承系统 `http_proxy` 环境变量。登录时走代理可能导致 502。
```bash
# 登录前关掉代理
http_proxy= https_proxy= HTTP_PROXY= HTTPS_PROXY= quarkpan auth login
```

### CLI命令
```bash
# 登录（生成二维码）- 先关代理！
http_proxy= https_proxy= quarkpan auth login

# 查看状态
QUARK_CONFIG_DIR="$(pwd)/config" quarkpan status

# 列出文件 - GET类可用
QUARK_CONFIG_DIR="$(pwd)/config" quarkpan ls /

# 创建文件夹
QUARK_CONFIG_DIR="$(pwd)/config" quarkpan mkdir /小墨备份/

# ⚠️ 上传不可用（已知bug），参见上述替代方案
```

### 存储限制
- 个人用户空间：通常10TB
- 免费版可能有上传速度/大小限制
- 通过Cookie认证，没有标准OAuth token过期机制

---

## 跨云盘策略

### 当前配置（Keke's setup）
| 云盘 | 容量 | 状态 | 说明 |
|:----|:----|:-----|:-----|
| 百度网盘 | 16TB | 已授权待审核 | 列文件可用，上传需等7天 |
| 夸克网盘 | 10TB | 已扫码可用 | 扫码即用，作为临时替代 |

### 备份建议
- 百度网盘审核通过前 → 备份存夸克
- 百度网盘审核通过后 → 主备份存百度，夸克做备用
- 大文件(>1GB)建议分片上传
- Token过期前自动刷新（百度30天，夸克Cookie可能更长）
