# Chinese TTS Voice Quality Reference

## Edge TTS (Free, Default)
| Voice ID | Name | Quality | Notes |
|----------|------|---------|-------|
| `zh-CN-YunxiNeural` | 云希 | ⭐⭐⭐ | Male, natural Chinese, current default |
| `zh-CN-XiaoxiaoNeural` | 晓晓 | ⭐⭐⭐ | Female, sweet and clear |
| `zh-CN-YunjianNeural` | 云健 | ⭐⭐ | Male, more youthful, slightly robotic |
| `zh-CN-YunyangNeural` | 云扬 | ⭐⭐ | Male, deeper but less natural |
| `en-US-AriaNeural` | Aria | ⭐⭐ | English female — NOT for Chinese (old default) |

## ElevenLabs (Paid, API Key stored)
**Key finding: ElevenLabs premade voices are ALL English-native.** Even with `eleven_multilingual_v2` model, they sound like foreigners speaking Chinese. Not suitable for natural Chinese speech.

- API Key: `sk_18bd08aa589d83391dbe1c859c090f041b4e7b43d1af68b2` (stored in `.env` as `ELEVENLABS_API_KEY`)
- Voice ID configured: `pNInz6obpgDQGcFmaJgB` (Adam — American male, sounds foreign in Chinese)
- Free tier: 10,000 chars/month
- [elevenlabs.io] 🇨🇳 **需要翻墙** — blocked from mainland China

## Current Default
**Edge TTS zh-CN-YunxiNeural** — set in `config.yaml` at `tts.edge.voice`

Keke tested and approved this voice. Do not switch without asking.

## LipVoice (lipvoice.cn)
- Domestic Chinese voice cloning service 🇨🇳 国内直连
- Model "小墨-ls" created (Keke's account, 139****7760)
- API requires enterprise membership (¥499/year) — not set up yet
- For now, only usable via web interface for manual TTS generation
