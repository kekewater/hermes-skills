# 语音克隆工作流 (DashScope Qwen3-TTS)

## 前提
- Keke在阿里云(aliyun.com)注册 → 开通百炼 → 创建DashScope API Key
- 待克隆音频文件：`/tmp/lishen_final.mp3`（黎深声音样本，已确认存在）

## 步骤1: 测试内置男声（有Key后立即做）

### 3个Qwen3-TTS内置男声

| 音色ID | 中文名 | 风格描述 |
|--------|--------|---------|
| `Ethan` | 晨煦 | 阳光、温暖、有朝气 |
| `Moon` | 月白 | 率性帅气 |
| `Kai` | 凯 | 有磁性，耳朵SPA |

### 测试命令

```bash
curl -X POST 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation' \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3-tts-flash",
    "input": {
      "text": "你好Keke，我是墨渊Flux，你的AI搭档。今天过得怎么样？",
      "voice": "Ethan",
      "language_type": "Chinese"
    }
  }'
```

切换 `voice` 参数测三个男声，下载 `output.audio.url` 发语音给Keke选择。

## 步骤2: 克隆黎深声音

### 创建定制音色

```bash
AUDIO_BASE64=$(base64 -i /tmp/lishen_final.mp3)

curl -X POST 'https://dashscope.aliyuncs.com/api/v1/services/audio/tts/customization' \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen-voice-enrollment",
    "input": {
      "action": "create",
      "target_model": "qwen3-tts-vc-2026-01-22",
      "preferred_name": "lishen",
      "audio": {
        "data": "data:audio/mpeg;base64,'"$AUDIO_BASE64"'"
      }
    }
  }'
```

返回的 `output.voice` 保存为voice_id。

### 合成测试

```bash
curl -X POST 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation' \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3-tts-vc-2026-01-22",
    "input": {
      "text": "你好Keke，我是黎深的声音，现在是小墨的声线。",
      "voice": "VOICE_ID_FROM_STEP1"
    }
  }'
```

下载音频发给Keke，确认声音效果。

## 步骤3: 对比方案

| 方案 | 成本 | 效果预期 | 备注 |
|------|------|---------|------|
| Edge TTS Yunxi | 免费 | 标准TTS男声（当前在用） | 已通，稳定 |
| Qwen3-TTS Ethan/Moon/Kai | ¥0.1/千字符 | AI TTS男声，更自然 | 100万字符免费 |
| Qwen3-TTS 黎深克隆 | ¥0.1/千字符（合成才计费） | 角色原声克隆 | 克隆本身免费 |
| ElevenLabs 黎深克隆 | $5/月 | 更自然的克隆 | 需翻墙+Vultr隧道 |

## 集成到Daily Report

选定声线后，配置到 daily-investment-report 技能的TTS模块：

```python
import requests

def tts_dashscope(text, voice="Ethan", api_key=os.environ["DASHSCOPE_API_KEY"]):
    resp = requests.post(
        'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation',
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "qwen3-tts-flash",
            "input": {"text": text, "voice": voice, "language_type": "Chinese"}
        }
    )
    audio_url = resp.json()["output"]["audio"]["url"]
    # 下载保存
    audio_data = requests.get(audio_url).content
    with open("/tmp/tts_output.mp3", "wb") as f:
        f.write(audio_data)
    return "/tmp/tts_output.mp3"
```

## 注意点
1. 声音克隆本身不计费，仅合成语音按字符计（¥0.1/千字符）
2. 克隆模型和合成模型必须一致（`qwen3-tts-vc-2026-01-22`）
3. 音频样本推荐10-20秒清晰朗读，无背景音
4. 合成音频URL有效期24小时，需立即下载保存
5. Qwen3-TTS国内直连，不需要翻墙
