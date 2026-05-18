# AgentMail 首次设置日志 (2026-05-16)

## 背景
Keke想要我有个自己的邮箱地址。最初我建议方案A（Himalaya + QQ邮箱IMAP/SMTP），但Keke自己发现了AgentMail并完成了注册。

## 设置过程

### 1. Keke注册
- Keke在 https://console.agentmail.to 注册账号
- 创建收件箱 → 分配了 `xiao-mo-keke@agentmail.to`
- 生成 API Key: `am_us_7bd6831fbba7c6996f0c60bce223865babf26d147747044befea0c5fc68374f1`

### 2. API测试

**关键发现：API版本号是 v0 不是 v1**
- https://api.agentmail.to/v1/* → 404
- https://api.agentmail.to/v0/* → 200

### 3. 发送测试
POST `/v0/inboxes/{inbox}/messages/send` 成功。发送者显示为 AgentMail。

### 4. 收信验证
Keke从 Gmail (jyt522@gmail.com) 发了测试信，API 读取成功。

### 5. 消息ID编码坑
消息ID `<CAO...@mail.gmail.com>` 中的 `<` `>` `@` `+` `=` 必须 URL 编码。
```python
import urllib.parse
encoded = urllib.parse.quote(message_id, safe='')
```

### 6. 关键认知：AgentMail vs 文件传输

Keke尝试通过微信发送EPUB文件（61MB），但WeChat iLink gateway可能没有可靠地保存附件到磁盘。AgentMail的诞生恰好填补了这个缺口：

- **AgentMail是邮件服务，不是文件存储** — 不要试图用邮件传输大文件（>25MB）或做备份存储
- **作为WeChat的补充通道** — 如果WeChat文件传输失败，可以让Keke通过AgentMail发送小文件
- **备份文件（65~125MB）不适合邮件** — 用disaster-recovery skill的备份方案

### 7. 首次成功的收发测试

- 📤 发信：POST `/v0/inboxes/xiao-mo-keke@agentmail.to/messages/send` → Keke的QQ邮箱成功收到
- 📥 收信：Keke从Gmail发测试信 → API读取成功
- ✅ 收件箱准确率：1/1 邮件正常收取，无遗漏
