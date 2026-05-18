# Voice STT (Speech-to-Text) Setup

**faster-whisper** local STT engine configuration for Hermes Agent on China server.

## When to Use

- Setting up voice recognition for the first time
- Troubleshooting STT engine not working
- Re-downloading the whisper model
- Checking voice configuration

## Installation

### System Dependencies

```bash
sudo apt install -y portaudio19-dev ffmpeg libopus0 espeak-ng
```

### Python Dependencies

```bash
pip install "hermes-agent[voice]" "hermes-agent[messaging]"
```

The `[voice]` extra installs faster-whisper and sounddevice.

## Model Download

The STT engine uses faster-whisper models from HuggingFace. On a China server, HF is slow through proxy. Use hf-mirror.com (domestic mirror, no proxy needed):

```bash
# Create model directory
mkdir -p ~/.cache/whisper/tiny
cd ~/.cache/whisper/tiny

# Download model files from Chinese mirror
wget https://hf-mirror.com/Systran/faster-whisper-tiny/resolve/main/config.json
wget https://hf-mirror.com/Systran/faster-whisper-tiny/resolve/main/vocabulary.txt
wget https://hf-mirror.com/Systran/faster-whisper-tiny/resolve/main/tokenizer.json
wget https://hf-mirror.com/Systran/faster-whisper-tiny/resolve/main/model.bin
```

The `model.bin` is ~75MB for the tiny model. Available model sizes:

| Model | Size | Speed | Accuracy |
|:------|:----:|:-----|:---------|
| tiny | 75MB | Fastest | Basic |
| base | 150MB | Fast | Good |
| small | 500MB | Medium | Better |
| medium | 1.5GB | Slow | Best |

## Configuration

### config.yaml

```yaml
stt:
  enabled: true
  provider: local
  local:
    model: tiny    # or: base, small, medium
```

The `stt:` section should be at the top level of config.yaml. The model config determines which model name faster-whisper will try to load (from ~/.cache/whisper/).

### .env (optional overrides)

```
# VOICE_TOOLS_OPENAI_KEY=   # For OpenAI Whisper API
# GROQ_API_KEY=              # For Groq Whisper (free)
# STT_GROQ_MODEL=whisper-large-v3-turbo
# STT_OPENAI_MODEL=whisper-1
```

## Testing

### Verify model loads correctly:

```bash
source ~/.whisper_venv/bin/activate
python3 -c "
from faster_whisper import WhisperModel
model = WhisperModel('/home/ubuntu/.cache/whisper/tiny', device='cpu', compute_type='int8')
# Language detection works
segments, info = model.transcribe(some_audio, beam_size=1, language='zh')
print(f'Language: {info.language} ({info.language_probability:.2f})')
"
```

### Test TTS (text-to-speech):

```bash
hermes tts test "你好，语音控制已启动"
```

## Model Cache Location

```
~/.cache/whisper/
├── CACHEDIR.TAG
├── tiny/                          # Manual download location
│   ├── config.json
│   ├── tokenizer.json
│   ├── vocabulary.txt
│   └── model.bin                  # ~75MB
└── models--Systran--faster-whisper-tiny/    # HF Hub cache (if used)
```

## Pitfalls

1. **Download from HuggingFace directly is slow** through Vultr proxy (~30KB/s). Always use `hf-mirror.com` for China servers.
2. **faster-whisper != openai-whisper**. The `[voice]` dependency installs faster-whisper (CTranslate2-based, much faster). They use different model formats.
3. **Model path must be absolute** when loading from manual download: `WhisperModel('/home/ubuntu/.cache/whisper/tiny', ...)` not just `WhisperModel('tiny', ...)` if you downloaded manually.
4. **No audio output needed** for WeChat voice transcription. The STT engine only needs to transcribe incoming voice messages, not produce audio.
5. **Memory**: tiny model uses ~500MB RAM during inference. On a 3.6GB server, this is fine for occasional use.
