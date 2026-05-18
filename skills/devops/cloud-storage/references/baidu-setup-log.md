# 百度网盘设置过程记录 (2026-05-16)

## 账号信息
- 开发者账号：可可water (已认证个人开发者)
- App名称：小墨网盘备份
- AppID: 123328717
- 硬件类型：软件
- 当前状态：**未审核**（需提交上线审核）

## 授权过程
1. 设备码模式授权，scope=basic,netdisk
2. QR二维码通过微信发给Keke扫码
3. 轮询获取access_token + refresh_token
4. Token有效期30天，自动续期脚本可用

## 回调地址
- 已配置: https://openapi.baidu.com/oauth/2.0/token
- 1小时后生效

## 已确认工作
- ✅ 查看网盘容量 (16TB / 已用1.8TB)
- ✅ 列目录 (GET method=list)
- ✅ 创建文件夹 (POST method=create, isdir=1)
- ✅ Precreate (POST method=precreate, 返回uploadid)
- ❌ 文件上传 (PCS API返回31064 "file is not authorized")
- ❌ Create (因上传没完成而失败, errno=31500)

## 应用审核
- 演示视频已生成：/tmp/baidu_demo_video.mp4 (19秒终端风格)
- Keke已提交审核，预计7个工作日
- 审核通过前：使用夸克网盘做临时备份

## 注意事项
- PCS上传API和xpan文件API是不同的子系统
- D.PCS.BAIDU.COM 需要额外的权限配置（审核通过后才能用）
- 即使审核通过后，上传也需要分片 (precreate→upload→create)
- Refresh Token只能用一次，每次刷新都会返回新的