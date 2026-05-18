# STT Model Download via hf-mirror.com (China Network)

When setting up `faster-whisper` for local STT on a China-based server, HuggingFace is blocked. The official `hf-mirror.com` mirror works for downloading model files.

The built-in `WhisperModel()` download via `huggingface_hub` may fail even with `HF_ENDPOINT=https://hf-mirror.com` due to SSL/config issues. **Direct `wget` is more reliable.**

## Steps

```bash
# 1. Install faster-whisper
pip install faster-whisper

# 2. Download model files from hf-mirror.com (no proxy needed from China)
MODEL=tiny  # or base, small, medium, large-v3
mkdir -p ~/.cache/whisper/$MODEL
cd ~/.cache/whisper/$MODEL

wget -q -t 3 https://hf-mirror.com/Systran/faster-whisper-$MODEL/resolve/main/config.json
wget -q -t 3 https://hf-mirror.com/Systran/faster-whisper-$MODEL/resolve/main/vocabulary.txt
wget -q -t 3 https://hf-mirror.com/Systran/faster-whisper-$MODEL/resolve/main/tokenizer.json
wget -q -t 3 https://hf-mirror.com/Systran/faster-whisper-$MODEL/resolve/main/model.bin

# 3. Configure Hermes
# config.yaml:
# stt:
#   enabled: true
#   provider: local
#   local:
#     model: tiny  # match the model you downloaded

# 4. Test
source ~/.whisper_venv/bin/activate  # if using venv
python3 -c "
from faster_whisper import WhisperModel
model = WhisperModel('~/.cache/whisper/$MODEL', device='cpu', compute_type='int8')
print('STT model loaded successfully')
"
```

## Model Sizes

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny | ~75MB | Fastest | Basic |
| base | ~150MB | Fast | Good |
| small | ~500MB | Moderate | Better |
| medium | ~1.5GB | Slow | Best (recommended for Chinese) |
| large-v3 | ~3GB | Slowest | State-of-art |

For Chinese voice recognition, `base` or `small` is recommended. `tiny` works but may miss words.
