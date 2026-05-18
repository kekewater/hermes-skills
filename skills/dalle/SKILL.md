---
name: dalle-chatgpt
description: Generate DALL·E 3 images via ChatGPT web interface (free tier) through US proxy server
category: image-generation
---

# DALL·E 3 Image Generation via ChatGPT Web (Free Tier)

Uses a US VPS (66.42.97.175, Los Angeles) with Playwright to log into free ChatGPT and generate images via DALL·E 3.

## Prerequisites

- US VPS `66.42.97.175` with SOCKS5 proxy on port 1080
- Playwright + Chromium installed on US server
- ChatGPT session cookies saved at `/home/ubuntu/.hermes/skills/dalle/chatgpt_cookies.json`
- SSH key: `/home/ubuntu/.ssh/id_vultr`

## Generating an Image

Call the generation script:

```python
from hermes_tools import terminal
result = terminal(f'python3 /home/ubuntu/.hermes/skills/dalle/scripts/generate.py "{prompt}"')
```

The script returns a JSON result with the image path.

## Parameters

- `prompt` (required): The image description in Chinese or English
- Output: PNG image saved to the local cache directory

## Limitations

- Free ChatGPT has limited DALL·E generations per day (~5-10)
- Generation takes 15-30 seconds
- Images are 512x512 or 1024x1024 depending on free tier
- The US server must be running
