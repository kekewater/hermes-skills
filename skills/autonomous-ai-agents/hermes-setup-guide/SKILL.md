---
name: hermes-setup-guide
description: 新手安装和配置Hermes Agent的完整引导。包含Provider配置、API Key获取、代理设置、常见错误排障。适用于新用户首次部署Hermes后的配置步骤。
version: 1.1.0
---

# Hermes Agent 新手配置引导

## 安装Hermes
```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

## 安装技能包
```bash
hermes skills tap add kekewater/hermes-skills
```
之后 `/skill <技能名>` 即可加载使用。

## 配置 API Key

```bash
hermes config edit
```

### Provider 配置要点

#### DeepSeek（默认聊天模型，最便宜）
```yaml
deepseek:
  base_url: https://api.deepseek.com/v1
  api_key: "sk-你的key"
  model: deepseek-v4-flash
  api_mode: deepseek-v4-flash
```
- 国内站：platform.deepseek.com，邮箱注册
- 🇨🇳 国内直连，不用翻墙

#### OpenAI（生图/备用）
```yaml
openai:
  base_url: https://api.openai.com/v1
  api_key: "sk-你的key"
  model: gpt-4o
  api_mode: openai    # ⚠️ 必须写这一行！
```
- ⚠️ `api_mode: openai` 必须写。不写的话Hermes会发自己的自定义参数，OpenAI返回400错误"Encrypted content is not supported"
- 🇺🇸 美国服务器直连；🇨🇳 国内服务器需要配代理

#### 阿里云百炼（TTS语音合成/图片识别）
```yaml
dashscope:
  base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
  api_key: "sk-你的key"
  model: qwen2.5-vl-72b-instruct
  api_mode: dashscope
```
- 控制台：dashscope.console.aliyun.com
- 🇨🇳 国内直连，新用户100万字符免费

#### OpenRouter（接Claude等模型）
```yaml
openrouter:
  base_url: https://openrouter.ai/api/v1
  api_key: "sk-or-你的key"
  model: anthropic/claude-sonnet-4
```
- 🇨🇳 国内需翻墙

### 默认模型设置
```yaml
model:
  default: deepseek-v4-flash
  provider: deepseek
```

## 测试配置

```bash
# 测试DeepSeek
hermes chat -q "你好"

# 测试OpenAI
hermes chat -q "你好，用OpenAI回复" --provider openai

# 查看provider列表和状态
hermes tools list
```

## 常用技能

| 技能名 | 用途 | 加载方式 |
|--------|------|---------|
| `china-stock-data` | A股实时行情/财务 | /skill china-stock-data |
| `us-stock-data` | 美股实时/财报 | /skill us-stock-data |
| `dcf-model` | DCF估值建模 | /skill dcf-model |
| `comps-analysis` | 可比公司分析 | /skill comps-analysis |
| `daily-investment-report` | 每日投资日报 | /skill daily-investment-report |
| `dashscope` | 阿里云TTS/生图 | /skill dashscope |
| `sec-filings` | SEC财报抓取 | /skill sec-filings |

## 常见错误

### ❌ "Encrypted content is not supported"
**原因：** OpenAI provider没设 `api_mode: openai`。
**修复：** 在provider配置里加上 `api_mode: openai`。

### ❌ 用 `provider: custom` 连OpenAI报400
**原因：** custom provider会发自定义参数，OpenAI不认。
**修复：** 不要用 `provider: custom`，改用 `provider: openai` + `api_mode: openai`。参考上面的配置模板。

### ❌ gpt-image-2 生图报错（chat completions返回500 / responses API说model不存在）
**原因：** gpt-image-2不走 chat completions 也不走 responses API，它走的是 `/v1/images/generations` 端（跟DALL-E同一个端）。
**正确调用方式：**
```bash
curl -s -X POST https://api.openai.com/v1/images/generations \
  -H "Authorization: Bearer 你的Key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2-low",    # low(~15s) / medium(~40s) / high(~2min)
    "prompt": "一只橘猫在书桌前看书",
    "n": 1,
    "size": "1024x1024",           # 1536x1024(横) / 1024x1024(方) / 1024x1536(竖)
    "quality": "low"
  }'
```
返回的是 `data[0].b64_json`，需要 base64 解码存成图片文件。

### ❌ OpenAI 401 / Auth失败
**原因：** API Key填错或已过期。
**修复：** 去 platform.openai.com/api-keys 重新创建Key。

### ❌ gpt-image-2 图片太长没生成出来
**原因：** 提示词(prompt)太长了，中文建议控制在200字以内。
**修复：** 缩短prompt，或者拆分成多次生成。也可以降低 quality 为 low（最快~15秒）。

### ❌ DeepSeek连不上
**原因：** 国内网络问题或Key失效。
**修复：** 确认 `base_url: https://api.deepseek.com/v1` 正确。

### ❌ "User not found" / 401 (OpenRouter)
**原因：** OpenRouter API Key过期。
**修复：** 去 openrouter.ai/keys 重新生成。

### ❌ dotenv 依赖错误
```bash
pip install python-dotenv
```

### ❌ 技能不显示
```bash
hermes skills list          # 查看已安装技能
hermes skills tap add kekewater/hermes-skills   # 重新添加源
```

## 切换模型

对话中输入 `/model` 可交互式切换。或启动时指定：
```bash
hermes --provider openai --model gpt-4o
```
