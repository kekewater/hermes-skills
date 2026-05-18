---
name: web-search
version: 1.1.0
description: 联网搜索能力 — Tavily API的配置和使用。Hermes Agent所需的搜索API Key配置、工具启用和常用搜索模式。
author: xiao-mo-keke (墨渊/Flux)
category: devops
---

# Web Search (联网搜索)

## Overview

Hermes Agent的联网搜索能力通过 Tavily API 提供。Tavily是专为AI Agent设计的搜索API，返回结构化搜索结果（标题、摘要、链接、来源等）。

## Setup

### 1. 获取 API Key

1. Keke在浏览器打开 https://tavily.com
2. 点 "Get Started" 或 "Sign Up"
3. 用QQ邮箱注册（国内直连，**不需要翻墙** — 已验证 HTTP 200）
4. 选 **Free Tier**（每月1000次搜索，免费）
5. 复制tvly-开头的API Key

### 2. 配置到 Hermes

**凭证文件：** `~/.config/tavily/credentials.json`
```json
{"api_key": "tvly-dev-xxxxx"}
```

**环境变量**（必须写入 `~/.hermes/.env`，仅shell环境变量不够——Gateway进程不继承shell env）：
```
TAVILY_API_KEY=tvly-dev-xxxxx
```

⚠️ **常见误区：** 只把Key存到 `~/.config/tavily/credentials.json` 而没写入 `.hermes/.env`，会导致 **CLI模式可用但Gateway（微信等消息平台）模式不能用**。因为Gateway是独立进程，不读取shell的环境变量。写入 `.env` 后需要重启gateway才能生效。

### 3. 启用工具集

```bash
hermes tools enable web
```

注意：工具变更需要在 `/reset` 新会话后生效。

### 4. 测试（无需等新会话）

直接通过Tavily REST API测试（API Key从credentials.json读取测试）：

```bash
API_KEY=$(python3 -c "import json; print(json.load(open('$HOME/.config/tavily/credentials.json'))['api_key'])")
curl -s -X POST "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -d "{\"api_key\": \"$API_KEY\", \"query\": \"test\", \"search_depth\": \"basic\", \"include_answer\": true}"
```

- tavily.com/api 从国内直连不需要代理（已验证 HTTP 200 via both direct and proxy）
- `search_depth: basic` = 快但浅，`advanced` = 慢但深
- `include_answer: true` 会返回AI摘要
- 返回结构：results[]（含title/url/content/score）+ response_time + answer
- 每条结果的score从0到1表示相关性

### 5. 验证Gateway也能用

如果通过微信/Telegram等Gateway使用Hermes，重启gateway后在新对话查看是否能调web_search工具：
```bash
hermes gateway restart
```

## 使用场景

| 优先级 | 场景 | 说明 |
|:-----:|:----|:----|
| 🔴 | 查正在看的内容最新数据 | 历史人物、公司/行业现况、政策法规 |
| 🔴 | 查平台规则/API文档 | 新入驻平台的terms、API用法 |
| 🟡 | 市场调研 | Amazon书籍市场、AI行业趋势 |
| 🟡 | 写作资料核实 | 历史日期、地点、人名准确性 |
| 🟢 | 技术问题排查 | 错误信息搜索、库文档查找 |

## 用量控制

- 免费额度：1000次/月（约33次/天）
- 我的实际用量：不是所有对话框都需要搜索
- 每次搜索前先判断：这个问题我训练数据里知道吗？知道就不用搜
- 节省策略：能凭记忆回答的不用搜，搜不到最新信息的不用反复搜

## 已知限制

- Tavily是独立的搜索API，不是浏览器打开网页
- 搜索结果不含JavaScript渲染的内容
- 不适合需要登录的站内搜索
- 与 `web` 工具集配合使用
