# Vision Configuration Guide

Hermes Agent 的视觉能力通过 `auxiliary.vision` 配置实现。当当前模型不支持图片输入时，可以配置一个单独的视觉模型作为辅助。

## 前提条件

- 一个支持多模态输入的模型/API（如 GP通义千问 qwen-vl-max、GPT-4o、Google Gemini 等）
- 对应的 API Key

## 配置步骤

### 0. 先配置 provider（重要！仅设 auxiliary.vision 不够）

仅设 `auxiliary.vision` 不会自动注册 provider，视觉请求会路由到主模型（如 DeepSeek）导致报错。必须先显式添加 provider：

```bash
hermes config set providers.dashscope.base_url https://dashscope.aliyuncs.com/compatible-mode/v1
hermes config set providers.dashscope.model qwen2.5-vl-72b-instruct
hermes config set providers.dashscope.api_mode dashscope
# API Key 在 .env 中设置：DASHSCOPE_API_KEY=sk-xxx
```

### 1. 确保 vision 工具集已启用

```bash
hermes tools list | grep vision
# 如果未启用：hermes tools enable vision
```

### 2. 配置辅助视觉模型

```bash
# ⭐ 推荐：使用阿里云通义千问视觉模型（国内直连，无需翻墙）\nhermes config set auxiliary.vision.provider dashscope\n# qwen2.5-vl-72b-instruct 经测试可正常看图分析\nhermes config set auxiliary.vision.model qwen2.5-vl-72b-instruct\n# qwen-vl-max 是旧版模型名，也可用但能力略弱\n# 设置 API Key：在 ~/.hermes/.env 中添加 DASHSCOPE_API_KEY=sk-xxx

# 示例：使用 OpenAI GPT-4o
hermes config set auxiliary.vision.provider openai
hermes config set auxiliary.vision.model gpt-4o

# 示例：使用 Google Gemini
hermes config set auxiliary.vision.provider google
hermes config set auxiliary.vision.model gemini-2.0-flash
```

### 3. 配置通用辅助模型（vision 会自动 fallback）

```bash
# 如果不单独配 vision，可以配通用 auxiliary
export OPENROUTER_API_KEY="sk-or-xxx"  # 或任意支持多模态的 provider
hermes config set auxiliary.model gpt-4o
hermes config set auxiliary.provider openai
```

### 4. 重启生效

```bash
hermes restart          # gateway 模式
# 或直接退出后重新进入 CLI 模式
```

## 测试

发送一张图片给 Hermes，如果配置正确，辅助视觉模型会自动处理图片分析。

也可手动测试 API 连通性：

```bash
# 测试 DashScope（国内推荐）
curl -X POST "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions" \
  -H "Authorization: Bearer sk-your-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-vl-72b-instruct",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "回复"API通了""},
        {"type": "image_url", "image_url": {"url": "https://example.com/test.jpg"}}
      ]
    }]
  }'
```

## 故障排查

| 问题 | 检查点 |
|------|--------|
| `unknown variant 'image_url'` | 当前模型不支持图片，需配置 auxiliary.vision |
| 视觉分析返回空 | `vision_tools` 是否已启用？ `hermes tools list` |
| 403 错误 | API Key 是否有效？余额是否充足？ |
| 500 Internal Server Error | OpenRouter 可能被国内网络干扰，换 DashScope 试试 |
| 超时 | 视觉模型响应可能较慢，增加 timeout 配置 |
| **配置了auxiliary.vision仍走主模型** | 可能需要在config.yaml中添加 `providers.dashscope` 条目（含 base_url / api_key / model），重启后生效 |

## 国内 vs 境外方案对比

| 方案 | 国内直连 | 价格 | 推荐场景 |
|:---|:---:|:---:|:---|
| **DashScope (通义千问)** ⭐ | ✅ | ~0.3分/千token | 国内首选，注册即送额度 |
| 推荐模型：`qwen2.5-vl-72b-instruct`（实测可用，看图精细）或 `qwen-vl-max` |
| **智谱 GLM-4V** | ✅ | ~1分/千token | 备选，open.bigmodel.cn |
| **腾讯混元** | ✅ | 新用户免费 | 需腾讯云账号 |
| **OpenRouter** | ❌ 500错误 | 按量计费 | 从中国直连不可用，需境外代理 |
| **Google Gemini** | ❌ 被墙 | 免费 | 需境外代理/Vultr转发 |

## 备选方案：OCR

如果当前不具备配置视觉模型的条件，可用 OCR 方案：

1. **Tesseract OCR**（已安装）：适合中文文字提取
2. **EasyOCR**（需安装）：基于 PyTorch，中文识别效果好
3. **PaddleOCR**（需安装）：百度方案，中英混合场景优秀

详见 `image-recognition` 技能。
