# quarkpan 上传 Bug & 替代方案 (v1.0.5)

## 已知 Bug: NoSuchBucket 上传失败

### 症状
quarkpan upload 命令报 404 NoSuchBucket 错误：
```
❌ 上传文件失败: 上传分片 1 失败: 404 NoSuchBucket
<Code>NoSuchBucket</Code>
<Message>The specified bucket does not exist.</Message>
<HostId>ul-sz.oss-cn-shenzhen.aliyuncs.com</HostId>
<BucketName>ul-sz</BucketName>
```
或 bucket 名变为 `ul-sz-acc`。

### 根因
quarkpan 的 `_pre_upload()` 调用 `file/upload/pre` API，返回的 bucket 名与实际阿里云 OSS bucket 不匹配。`_get_upload_auth()` 直接使用该 bucket 名构造上传 URL 到 `{bucket}.oss-cn-shenzhen.aliyuncs.com`，但该 bucket 实际不存在。

推测原因：
- 新注册账号可能分配到不同区域的 OSS 基础设施
- 夸克后端返回的 bucket 名仅供 SDK（浏览器/APP）内部路由使用，CLI 工具解析有误
- 该库自2024年起未见更新，接口可能已变更

### 诊断记录 (2026-05-16)
测试了所有主流阿里云 OSS 区域 endpoint（oss-cn-hangzhou/shanghai/qingdao/beijing/zhangjiakou/huhehaote/shenzhen/hongkong 等），均返回 `NoSuchBucket`。唯一异常是 `oss-accelerate.aliyuncs.com` 返回 `InvalidRequest: Transfer Acceleration is not configured` — 说明 `ul-sz` bucket 在阿里云系统中**确实存在**，但不属于 `oss-cn-shenzhen` 区域，且加速传输未开启。

这一行为说明：
- 从**中国境外 IP** 访问时，bucket 不可见（返回 NoSuchBucket）
- 通过 `oss-accelerate` 全球加速 endpoint 能识别 bucket 但加速未配置
- 真正的上传 endpoint 可能使用了阿里云内部路由或不同的 endpoint 格式

### 不影响的 API
- 登录（扫码获取 cookie） ✅
- 列出文件/目录 `ls` `list-dirs` ✅
- 查看状态 `status` ✅
- 创建/删除文件夹 `mkdir` `rm` ✅（未测试但应为 GET 类请求）

## 替代方案：浏览器上传

当 quarkpan upload 不可用时的操作路径：

### 方法 A：直连夸克网页版
1. 用 agent-browser 打开 `https://pan.quark.cn/`
2. 点「其他登录方式」→ 手机号短信登录（需要 Keke 输入手机号 + 验证码）
3. 登录后直接拖拽/选择文件上传

### 方法 B：生成分享链接转存
如果原文件已经存在于其他夸克账号或从网上下载：
- 生成分享链接 → 用 quarkpan 的 `save` 或 `batch-save` 命令
- 注意：此方法只测试过目录浏览，分享功能未验证

## 代理注意事项

```bash
# quarkpan 使用 httpx，会继承系统 http_proxy 环境变量
# 国内阿里云 OSS 走代理可能导致超时或 502
# 登录时需关掉代理：
http_proxy= https_proxy= HTTP_PROXY= HTTPS_PROXY= quarkpan auth login

# 列出目录可以不关代理（GET 请求）：
quarkpan ls /
```

## 配置目录位置

quarkpan 的 `get_config_dir()` 默认返回 `Path.cwd() / 'config'`，即当前工作目录下的 `config/` 文件夹。

```python
# 源码位于 quark_client/config.py line 18
return Path.cwd() / 'config'
```

**解决方法**：使用环境变量 `QUARK_CONFIG_DIR` 指定配置目录：
```bash
QUARK_CONFIG_DIR="/path/to/config" quarkpan auth login
```
