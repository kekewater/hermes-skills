---
name: agentmail
description: AgentMail 邮件服务集成 — 收发邮件、管理线程、企业沟通
category: email
---

# AgentMail 邮件服务

## 概述
AgentMail 是专为 AI agent 设计的邮件 API 平台。我的邮箱 `xiao-mo-keke@agentmail.to`，API Key 存在 `.env` 的 `AGENTMAIL_API_KEY`。

**核心认知：AgentMail 是邮件通信，不是文件存储。** 不要试图把备份、大型数据集、数据库等塞进邮件里。发文件可以，但单封邮件+附件不宜超过25MB。

## API 基础
- **Base URL**: `https://api.agentmail.to/v0/`（⚠️ 是 v0 不是 v1）
- **认证**: `Authorization: Bearer $AGENTMAIL_API_KEY`
- **Content-Type**: `application/json`

## 可用端点

### 📨 收信
```bash
# 列出所有消息
curl -s "https://api.agentmail.to/v0/inboxes/xiao-mo-keke%40agentmail.to/messages" \
  -H "Authorization: Bearer $AGENTMAIL_API_KEY"

# 查看单条消息（message_id 需要 URL 编码，特别是 < 和 > 和 @ 符号）
curl -s "https://api.agentmail.to/v0/inboxes/xiao-mo-keke%40agentmail.to/messages/{URL_ENCODED_MESSAGE_ID}" \
  -H "Authorization: Bearer $AGENTMAIL_API_KEY"

# 查看线程
curl -s "https://api.agentmail.to/v0/inboxes/xiao-mo-keke%40agentmail.to/threads" \
  -H "Authorization: Bearer $AGENTMAIL_API_KEY"
```

### 📤 发信
```bash
curl -s -X POST "https://api.agentmail.to/v0/inboxes/xiao-mo-keke%40agentmail.to/messages/send" \
  -H "Authorization: Bearer $AGENTMAIL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["recipient@example.com"],
    "subject": "主题",
    "text": "正文内容"
  }'
```

### 🔄 回信
```bash
curl -s -X POST "https://api.agentmail.to/v0/inboxes/xiao-mo-keke%40agentmail.to/messages/reply" \
  -H "Authorization: Bearer $AGENTMAIL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "<原消息ID>",
    "text": "回复内容"
  }'
```

## 消息字段
- `message_id`: 消息唯一ID（如 `<CAO...EA@mail.gmail.com>`），URL编码后使用
- `thread_id`: 线程UUID
- `from`: 发件人
- `to`: 收件人数组
- `subject`: 主题
- `text`: 纯文本正文
- `html`: HTML正文
- `extracted_text`: 提取的纯文本
- `labels`: 标签（received, unread, sent, draft等）
- `senders`: 发件人列表
- `preview`: 预览文本
- `size`: 消息大小（字节）
- `timestamp`: ISO时间戳

## 存储限制与约束

| 限制项 | 数值 | 说明 |
|:------|:----|:-----|
| 单封邮件大小 | ~25MB（标准SMTP限制） | 含正文+附件总计 |
| 消息ID长度 | 可变，通常50-100字符 | 必须URL编码后使用 |
| 消息保留 | 跟随付费计划 | 免费计划可能有时限 |
| 附件支持 | ✅ 是 | 通过Attachment API |

**⚠️ 邮件不是文件存储方案。** 不要用 AgentMail 来：
- ❌ 保存备份文件（~65-125MB 远超合理邮件大小）
- ❌ 存储大型数据集或数据库
- ❌ 作为长期归档

**备份请用：** `disaster-recovery` skill 的方案（本地备份 + GitHub推送 + 百度网盘）

## Message ID 编码

AgentMail 的消息 ID 格式通常是 SMTP 标准格式如 `<xxx@domain.com>`。在URL中使用时，需要对 `<`、`>`、`@` 等特殊字符编码。

Keke的示例（已验证工作）：
```
message_id: <CAO7e6yL++WkLsqRDcX1-ReJ7hBOWbkx2nnkW6yGYh2zW+9E=EA@mail.gmail.com>
URL: .../messages/%3CCAO7e6yL++WkLsqRDcX1-ReJ7hBOWbkx2nnkW6yGYh2zW%2B9E%3DEA%40mail.gmail.com%3E
```

Python 编码方式：
```python
import urllib.parse
encoded = urllib.parse.quote(message_id, safe='')
```

## 常用场景

阅读未读邮件 → 线程列表查labels含'unread'的 → 读消息内容 → 按需回复

## API Reference

完整API端点文档见 `references/api-endpoints.md`（2026-05-16实测定稿）。

## 关键注意点

- **inbox_id** = 完整邮箱地址 `xiao-mo-keke@agentmail.to`
- **message_id** 含 `<`, `>`, `@` 字符，API路径中必须URL编码
- 发送 `to` 参数是数组格式 `["addr1@example.com"]`
- 发信成功返回 `{"message_id": "...", "thread_id": "..."}`
- 免费计划可能有发送频率限制
```python
import requests, os
KEY = os.environ['AGENTMAIL_API_KEY']
headers = {'Authorization': f'Bearer {KEY}'}

# 查未读线程
r = requests.get('https://api.agentmail.to/v0/inboxes/xiao-mo-keke@agentmail.to/threads', headers=headers)
threads = r.json()['threads']
unread = [t for t in threads if 'unread' in t['labels']]

# 读内容
for t in unread:
    inbox = 'xiao-mo-keke%40agentmail.to'
    mid = urllib.parse.quote(t['last_message_id'], safe='')
    r = requests.get(f'https://api.agentmail.to/v0/inboxes/{inbox}/messages/{mid}', headers=headers)
    msg = r.json()
    print(f"From: {msg['from']}\nSubject: {msg['subject']}\nBody: {msg['text']}")
```

## 发件人信息
当从 `xiao-mo-keke@agentmail.to` 发信时：
- 显示名称默认为 "AgentMail"
- 代发路径显示为 `010001...@mail.agentmail.to`（Amazon SES）
- 收件人可以正常回复到 `xiao-mo-keke@agentmail.to`

## 参考
- `references/agentmail-setup-log.md` — 首次设置的过程笔记
- 文档: https://www.agentmail.to/docs
