---
name: dashscope
description: Alibaba DashScope (通义千问/通义万相) API — image generation (wanx), vision analysis (Qwen-VL), TTS (text-to-speech), voice cloning (声音复刻), and voice design. Works from mainland China without VPN. Free tier available.
version: 1.1.0
metadata:
  hermes:
    tags: [dashscope, alibaba, qwen, tongyi, wanxiang, image-gen, vision, tts, voice-cloning, china-ai]
    related_skills: [image-recognition, comfyui]
---

# DashScope — 阿里云通义API

## Overview

**DashScope** (dashscope.aliyuncs.com) 是阿里云/阿里巴巴的大模型API平台，提供：
- **通义万相 (`wanx`)** — 文生图 (text-to-image)
- **通义千问视觉 (`qwen-vl-*`)** — 图片识别/理解
- **通义千问文本 (`qwen-*`)** — 文本对话/推理
- **语音合成 (TTS)** — 千问3-TTS / CosyVoice 系列，支持声音复刻和声音设计

**核心优势**：从中国大陆直连（无需VPN），有免费额度。

## Authentication

```bash
# .env 或环境变量
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

API Key 从 [DashScope 控制台](https://dashscope.console.aliyun.com/) 获取。

## Image Generation (通义万相)

### Async API (推荐)

通义万相只支持**异步任务**模式：

```bash
# 1. 提交任务
curl -s -X POST https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-DashScope-Async: enable" \
  -d '{
    "model": "wanx2.1-t2i-turbo",
    "input": {"prompt": "你的提示词"},
    "parameters": {"n": 1}
  }'

# 2. 查询结果（获取task_id后）
curl -s -X GET "https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}" \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY"
```

### Available Models

| Model ID | 说明 | 速度 |
|----------|------|------|
| `wanx2.1-t2i-turbo` | 通义万相2.1 Turbo版（快速） | ~15-25秒 |
| `wanx2.1-t2i-plus` | 通义万相2.1 Plus版（更精细） | ~30-60秒 |

### Parameters

| 参数 | 说明 | 示例 |
|------|------|------|
| `n` | 生成数量（默认4，设为1只生成1张） | `1` |
| `size` | ✅ 使用 `"size": "1024*1024"` 或 `{"width": 1024, "height": 1024}` | `1024*1024` |
| `prompt` | 提示词，中文效果很好 | `"一只橘猫在书桌前"` |

### ⚠️ `n` 参数行为

`n` 参数控制生成图片数量（默认4）。但注意：
- 极短/模糊的 prompt（如"一只橘猫"）时，即使设 `n: 1`，模型也可能自动生成多个变体
- 详细/结构化的 prompt（如长篇财经信息图描述）时，`n: 1` 通常只返回1张
- 如果需要确保只拿1张，取 `results[0]` 即可安全使用

### ⚠️ Size Parameter Pitfall

`"size": "1024x1024"` (小写x) **会报错** `"InvalidParameter: size is not in the correct format"`。

**正确格式**：
```json
// 格式1 — 推荐
{"parameters": {"n": 1, "size": "1024*1024"}}

// 格式2 — 也有效
{"parameters": {"n": 1, "width": 1024, "height": 1024}}
```

### Response Handling

```python
import json, time, requests

# 提交
resp = requests.post('https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis',
    headers={
        'Authorization': f'Bearer {api_key}',
        'X-DashScope-Async': 'enable'
    },
    json={
        'model': 'wanx2.1-t2i-turbo',
        'input': {'prompt': prompt},
        'parameters': {'n': 1, 'size': '1024*1024'}
    }
)
task_id = resp.json()['output']['task_id']

# 轮询（建议15-25秒后查询）
time.sleep(20)
resp = requests.get(f'https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}',
    headers={'Authorization': f'Bearer {api_key}'}
)
result = resp.json()
status = result['output']['task_status']  # 'SUCCEEDED', 'FAILED', 'PENDING', 'RUNNING'

if status == 'SUCCEEDED':
    image_url = result['output']['results'][0]['url']
    # 下载图片，URL有有效期（约5分钟）
    # !!! 务必立即下载保存 !!!
elif status == 'FAILED':
    error_code = result.get('code', '')
    error_msg = result.get('message', '')
```

### ⚠️ Critical: URL Expiration

图片下载链接 **有效期极短**（约5分钟），必须在结果返回后**立即下载**到本地：

```python
# 正确做法：立即下载
import requests
img_data = requests.get(image_url).content
with open('/home/ubuntu/hermes/cache/image.png', 'wb') as f:
    f.write(img_data)
```

### Prompt Tips

- 中文提示词效果很好，不需要翻译成英文
- 自动扩充prompt：通义万相会自己丰富细节
- 给长格式/结构化提示词时，模型会尽力排版但**不能保证文字精确性**
- 适合：视觉创意、概念图、氛围图
- **不适合**：精确文字排版、数据表格、图表中的精确数字
- **结构化prompt技巧**：给金融信息图等复杂排版时，用 `左侧面板：xxx | 中间面板：xxx | 右侧面板：xxx` 的分段描述能引导布局，但具体数字会被忽略或画错

## Image Understanding (视觉识别)

### Available Models

| Model ID | 优势 |
|----------|------|
| `qwen2.5-vl-72b-instruct` | ⭐ 实测最强，看图精细，可作为 Hermes auxiliary.vision 首选 |
| `qwen-vl-max` | 强，准确率高 |
| `qwen-vl-plus` | 性价比高 |

### Hermes 集成（auxiliary.vision）

在 config.yaml 中配置 DashScope 为辅助视觉模型：

```yaml
auxiliary:
  vision:
    provider: dashscope
    model: qwen2.5-vl-72b-instruct  # 或 qwen-vl-max
providers:
  dashscope:
    base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    api_key: <from .env>
    model: qwen2.5-vl-72b-instruct
```

.env:
```
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

重启后生效。browser_vision 工具会自动使用此模型分析截图。

### Usage

```bash
curl -s -X POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen-vl-max",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "描述这张图片"},
        {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
      ]
    }]
  }'
```

也支持 base64 图片数据：
```json
{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,<base64_data>"}}
```

## Text-to-Speech (语音合成)

DashScope 提供多系列 TTS 模型，支持非实时（HTTP）和实时（WebSocket）两种模式。

### Available Models

| 模型 | 系列 | 声音复刻 | 声音设计 | 指令控制 | 免费额度 |
|------|------|---------|---------|---------|---------|
| `qwen3-tts-flash` | Qwen3-TTS HTTP | ❌ | ❌ | ❌ | 100万字符/90天 |
| `qwen3-tts-instruct-flash` | Qwen3-TTS HTTP | ❌ | ❌ | ✅ | 同上 |
| `qwen3-tts-vc-*` | Qwen3-TTS HTTP | ✅ | ❌ | ❌ | 同上 |
| `cosyvoice-v3.5-plus` | CosyVoice | ✅ | ✅ | ✅ | 新用户免费3月 |
| `cosyvoice-v3.5-flash` | CosyVoice | ✅ | ✅ | ✅ | 同上 |
| `cosyvoice-v3-plus` | CosyVoice | ✅ | ✅ | ❌ | 同上 |
| `MiniMax/speech-2.8-hd` | MiniMax | ✅ | ❌ | ❌ | — |

### Pricing (千问3-TTS系列)

| 模型 | 计费单位 | 标准价格 | 免费额度 |
|------|---------|---------|---------|
| 千问3-TTS-Flash (全部) | 元/千字符 | **0.1元/千字符** | 开通后90天内100万字符 |
| CosyVoice (旧产品线) | 元/万字符 | **2.00元/万字符** (1汉字=2字符) | 新用户免费试用3个月 |

> 💡 新用户免费100万字符 ≈ 每天1000字播报，能用将近3年

### Built-in Chinese Male Voices

| 音色ID | 音色名 | 描述 | 支持模型 |
|--------|--------|------|---------|
| `Ethan` | 晨煦 | 阳光、温暖、活力、朝气的男性 | qwen3-tts-flash, cosyvoice |
| `Moon` | 月白 | 率性帅气的男性 | qwen3-tts-flash, cosyvoice |
| `Kai` | 凯 | 有磁性的男声，耳朵SPA | qwen3-tts-flash |
| `Nofish` | 不吃鱼 | 不会翘舌音的设计师（男） | qwen3-tts-flash |

### TTS API — Non-Streaming (HTTP)

**cURL:**
```bash
curl -X POST 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation' \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3-tts-flash",
    "input": {
      "text": "你好，我是小墨。今天天气真好。",
      "voice": "Ethan",
      "language_type": "Chinese"
    }
  }'
```

返回的 `output.audio.url` 可下载音频（有效期24小时）。

**Python (DashScope SDK):**
```python
import dashscope
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

response = dashscope.MultiModalConversation.call(
    model="qwen3-tts-flash",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    text="你好，我是小墨。",
    voice="Ethan",
    language_type="Chinese",
    stream=False
)
# response.output.audio.url 为下载链接
```

### TTS API — Streaming (WebSocket)

添加Header `X-DashScope-SSE: enable` 即可流式返回PCM音频（24000Hz, 单声道, 16bit）。

### Instruction Control (指令控制)

CosyVoice v3.5+ 和 qwen3-tts-instruct-flash 支持用自然语言指令控制语速、情感、语调：

```json
{
  "model": "cosyvoice-v3.5-plus",
  "input": {
    "text": "今天股市大涨。",
    "voice": "Ethan",
    "instructions": "语速偏快，语气兴奋，像新闻播报一样"
  }
}
```

指令维度：音调(高/中/低)、语速(快/中/慢)、情感(开朗/沉稳/温柔/严肃/活泼/治愈)、特点(磁性/清脆/沙哑/浑厚)

---

## Voice Cloning (声音复刻 — Qwen-TTS)

只需 **10-20秒音频样本**，即可生成高度相似的定制音色，无需模型训练。

### Step 1: 创建音色

```bash
# 上传音频base64或URL
AUDIO_BASE64=$(base64 -i /path/to/lishi.mp3)

curl -X POST 'https://dashscope.aliyuncs.com/api/v1/services/audio/tts/customization' \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen-voice-enrollment",
    "input": {
      "action": "create",
      "target_model": "qwen3-tts-vc-2026-01-22",
      "preferred_name": "zhangsan",
      "audio": {
        "data": "data:audio/mpeg;base64,'"$AUDIO_BASE64"'"
      }
    }
  }'
```

返回 `output.voice` 为 voice_id，保存此ID供后续使用。

### Step 2: 使用克隆音色合成语音

```bash
curl -X POST 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation' \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3-tts-vc-2026-01-22",
    "input": {
      "text": "你好，我是克隆出来的声音。",
      "voice": "YOUR_VOICE_ID"
    }
  }'
```

### Requirements

| 要求 | 说明 |
|------|------|
| 音频时长 | 推荐10-20秒，最长60秒 |
| 内容 | 至少5秒连续清晰朗读，无背景音/BGM |
| 语言 | 中文普通话（驱动模型支持多语言） |
| 有效期 | 创建后长期有效 |

---

## Voice Cloning (声音复刻 — CosyVoice)

CosyVoice 通过 URL 上传音频样本（需要可公开访问的音频URL或上传到OSS）：

```bash
curl -X POST 'https://dashscope.aliyuncs.com/api/v1/services/audio/tts/customization' \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "voice-enrollment",
    "input": {
      "action": "create_voice",
      "target_model": "cosyvoice-v3.5-plus",
      "prefix": "lishi",
      "url": "https://your-audio-url.wav"
    }
  }'
```

合成时使用 `model: "cosyvoice-v3.5-plus"` + `voice` 参数。

---

## Voice Design (声音设计)

无需音频样本，仅通过**文字描述**创建全新音色。适合没有录音素材的品牌定制、角色配音。

```json
{
  "model": "qwen-voice-enrollment",
  "input": {
    "action": "create",
    "target_model": "qwen3-tts-vd-2026-01-26",
    "preferred_name": "warm_male",
    "voice_prompt": "温暖的年轻男性声音，语速中等偏低，沉稳有力，适合新闻播报",
    "preview_text": "各位观众晚上好。"
  }
}
```

**CosyVoice 声音设计**（仅v3.5系列支持）：
```json
{
  "input": {
    "action": "create_voice",
    "target_model": "cosyvoice-v3.5-plus",
    "prefix": "brand_voice",
    "voice_prompt": "温柔的女声，语速缓慢",
    "preview_text": "您好，欢迎收听。"
  }
}
```

### 声音描述技巧

| 维度 | 描述示例 |
|------|---------|
| 年龄 | 儿童(5-12)、青少年(13-18)、青年(19-35)、中年(36-55)、老年(55+) |
| 语速 | 快速、中速、缓慢、偏快、偏慢 |
| 情感 | 开朗、沉稳、温柔、严肃、活泼、冷静、治愈 |
| 特点 | 有磁性、清脆、沙哑、圆润、甜美、浑厚、有力 |
| 用途 | 新闻播报、广告配音、有声书、动画角色、语音助手 |

### 实测工作流 (Lishen Clone)

当Keke提供了DashScope API Key后的具体操作步骤见 `references/voice-cloning-workflow.md`：
1. 先测3个内置男声（Ethan/Moon/Kai）让Keke选声线
2. 用 `/tmp/lishen_final.mp3` 克隆黎深声音
3. 对比选择日常TTS方案
4. 集成到Daily Report

### ⚠️ Voice Cloning Pitfalls

1. **复刻与合成模型必须一致** — 用 qwen3-tts-vc 复刻的必须用 qwen3-tts-vc 合成
2. **音频质量 > 音频长度** — 10秒清晰无噪声样本 > 60秒带背景音的样本
3. **CosyVoice v3.5+ 支持方言** — 普通话、粤语、四川话、河南话等
4. **声音设计描述** — 长度限制：CosyVoice ≤500字符，Qwen-TTS ≤2048字符
5. **北京地域 vs 国际** — 中国大陆服务用 `dashscope.aliyuncs.com`（北京地域）

---

## Pricing

### Image Generation (通义万相)

通义万相 (wanx2.1-t2i-turbo) 当前有免费额度（具体额度以DashScope控制台为准）。

### TTS (语音合成)

| 模型 | 计费 | 免费额度 |
|------|------|---------|
| 千问3-TTS系列 (全部Flash版) | 0.1元/千字符 | 新用户100万字符/90天 |
| CosyVoice (旧产品线) | 2.00元/万字符 | 新用户免费3个月 |
| MiniMax | 按量付费 | — |

### Voice Cloning

声音复刻创建音色本身**不计费**，仅合成的TTS按字符计费。

### 获取免费额度

1. 开通百炼平台（搜索"百炼"）
2. TTS/Qwen模型自动发放免费额度
3. 阿里云新用户 9 折优惠券可用

## Common Pitfalls

1. **Async required** — 通义万相**不支持同步调用**，必须加 `X-DashScope-Async: enable` 头部并使用异步任务API
2. **Size格式** — 不要用 `1024x1024`（小写x报错），用 `1024*1024` 或 `width/height` 对象
3. **URL过期** — 下载链接5分钟有效，必须立即下载保存
4. **文字不精确** — 通义万相是扩散模型（非GPT-4o），输出图片中的**文字可能模糊/错误**，不能用于精确文档排版
5. **Rate limit** — 短时间多次请求会触发 `Throttling.RateQuota`，等待片刻即可
6. **Vision模型可直连** — `qwen-vl-max/plus` 的API端点在兼容模式下支持多轮对话，可作为Hermes `auxiliary.vision` provider的备选
7. **不需VPN** — DashScope全部服务国内直连，比OpenRouter/Google更稳定
8. **免费额度有限** — 长期使用需关注配额消耗，可在DashScope控制台查看
9. **TTS复刻模型一致性** — 用 `qwen3-tts-vc` 复刻的声音必须用同系列模型合成，不可混用
10. **⚠️ 通义万相不适合精确中文文本渲染** — 作为扩散模型，wanx2.1-t2i-turbo 生成的图片中中文文字**完全随机乱码**。实测"投资日报"长 prompt 产出图片的标题和数据全是无意义文字。对于需要精确文字的信息图/日报图，应使用 **GPT-Image-2**（通过Vultr VPS直连OpenAI API）。通义万相适合：概念图、氛围图、风景图、创意视觉。**不适合**：带文字的数据图表、信息图、文档截图。
   - 测试确认：GLM-4V-Plus 和 Qwen-VL-Max 用同一套 base64 编码的图片数据
   - 通用 fallback 代码见 `references/dashscope-api-quickref.md`

## References

| 文件 | 内容 |
|------|------|
| `references/dashscope-api-quickref.md` | API接口速查表（含Python代码片段） |

官方文档：
- [非实时语音合成](https://help.aliyun.com/zh/model-studio/non-realtime-tts-user-guide)
- [声音复刻 (Qwen-TTS)](https://help.aliyun.com/zh/model-studio/voice-cloning-user-guide)
- [声音设计](https://help.aliyun.com/zh/model-studio/voice-design-user-guide)
- [模型选型](https://help.aliyun.com/zh/model-studio/tts-model/)
- [定价页](https://www.alibabacloud.com/help/zh/model-studio/model-pricing)

## Related Skills

| 技能 | 说明 |
|------|------|
| `comfyui` | 本地 Stable Diffusion 生图（离线，不依赖API） |
| `image-recognition` | 图片识别/OCR（含智谱GLM、通义千问等多方案） |
