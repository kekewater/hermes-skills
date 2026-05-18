# ChatGPT + DALL·E 3 Automation

## Overview

Automate ChatGPT login and DALL·E 3 image generation using Playwright Python from a US-based VPS. The key challenges are:
1. Cloudflare Turnstile on `chatgpt.com` — bypassed by running from a **US IP** (not China datacenter)
2. Email verification code during login — user must provide the code
3. DALL·E generates images server-side; extract via DOM after generation completes

## Prerequisites

- Playwright Python (`pip install playwright`)
- Chromium browser (`npx playwright install chromium`)
- US-based VPS (Vultr Los Angeles works well)
- ChatGPT free account (email + password, or Google SSO)

## Login Flow

### Step 1: Navigate to ChatGPT

```python
page.goto('https://chatgpt.com/auth/login', wait_until='domcontentloaded')
time.sleep(3)
```

The login page shows:
- "Continue with Google"
- "Continue with Apple"
- "Continue with phone"
- Email input + "Continue" button

### Step 2: Fill Email

```python
page.fill('input[type="email"]', 'user@example.com')
page.locator('button[type="submit"]').first.click()
time.sleep(5)
```

**If email is linked to Google SSO**: the page redirects to `accounts.google.com`. Ask the user for their Google password or use an alternative login method.

**If email is an OpenAI direct account**: the page goes to an email verification screen:

```
URL: https://auth.openai.com/email-verification
Text: "Enter the verification code we just sent to user@example.com"
```

### Step 3: Handle Verification Code

Ask the user to check their email and send you the 6-digit code:

```python
code = input("Enter verification code from email: ")
await page.fill('input:not([type="hidden"])', code)
await page.locator('button[type="submit"]').first.click()
time.sleep(5)
```

After successful verification, the page redirects to `https://chatgpt.com/` — user is logged in.

**Alternative**: Click "Continue with password" link to bypass email verification if the user knows their password.

### Step 4: Save Session Cookies

```python
cookies = await page.context.cookies()
json.dump(cookies, open('/tmp/chatgpt_cookies.json', 'w'))
```

Reuse these cookies on subsequent runs to avoid re-authentication.

## DALL·E 3 Image Generation

### Step 1: Navigate to DALL·E GPT

```python
await page.goto('https://chatgpt.com/g/g-pmuQfob8d-image-generator', wait_until='domcontentloaded')
time.sleep(5)
```

This URL loads the official DALL·E image generator GPT.

### Step 2: Fill Prompt

```python
prompt = page.locator('#prompt-textarea')
if await prompt.count() == 0:
    prompt = page.locator('[contenteditable="true"]')
await prompt.first.fill('一只可爱的橘猫戴着巫师帽站在星空下，数字艺术风格')
await asyncio.sleep(1)
```

### Step 3: Send and Wait

```python
send = page.locator('[data-testid="send-button"]')
await send.first.click()
print('Prompt sent! Waiting for image...')

# DALL-E typically takes 10-30s to generate
for i in range(30):
    await asyncio.sleep(2)
    imgs = await page.evaluate('''
        Array.from(document.querySelectorAll('img')).filter(img => 
            img.src && img.complete && img.naturalWidth > 100
        ).map(img => ({src: img.src, width: img.naturalWidth, height: img.naturalHeight}))
    ''')
    large_imgs = [img for img in imgs if img['width'] > 200]
    if large_imgs:
        print(f'Found {len(large_imgs)} images!')
        img_src = large_imgs[0]['src']
        break
```

### Step 4: Download Image via Fetch

DALL·E images are served from `https://chatgpt.com/backend-api/estuary/content?id=file-...&gizmo_id=g-pmuQfob8d&ts=...&p=gpp&sig=...`

Use `page.evaluate(fetch(...))` to get the image as base64 through the authenticated session:

```python
img_data = await page.evaluate(f'''
    fetch("{img_src}").then(r => r.blob()).then(blob => {{
        return new Promise((resolve) => {{
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.readAsDataURL(blob);
        }});
    }})
''')
# img_data is a data: URL like "data:image/png;base64,iVBOR..."
img_bytes = base64.b64decode(img_data.split(',')[1])
with open('/tmp/dalle_output.png', 'wb') as f:
    f.write(img_bytes)
```

## Alternative: Browser-AI-Bridge (Node.js Server)

**Browser-AI-Bridge** (`browser-ai-bridge` npm package) is an alternative approach — a Node.js REST API server that manages a persistent Playwright Chrome session and exposes endpoints for AI provider interaction.

### Setup
```bash
# Already installed at /home/ubuntu/browser-ai-bridge/
cd /home/ubuntu/browser-ai-bridge
cp .env.example .env
# Configure .env:
PORT=3333
CHROME_PROXY=http://127.0.0.1:8889
HEADLESS=true
LOG_LEVEL=info
```

### Launch
```bash
cd /home/ubuntu/browser-ai-bridge && CHROME_PROXY=http://127.0.0.1:8889 HEADLESS=true node src/index.js
```

On first launch, the setup wizard runs in non-interactive mode (HEADLESS=true). It creates provider sessions and saves Chrome profile to `/tmp/chrome_ai_debug/`.

### First-Run Login Requirement
The server starts and returns `Bad Gateway` until the provider (ChatGPT) is actually logged in:
- Chrome starts on port 9222
- Profile saved at `/tmp/chrome_ai_debug/` (has `Cookies`, `Login Data` files)
- If no valid ChatGPT session cookies exist, all `/api/ask` requests return `Bad Gateway`
- **Fix**: Keke needs to log in once via remote Chrome DevTools (SSH tunnel + browser)

### API Usage
```bash
# Ping
curl http://localhost:3333/api/ping
# → {"status":"ready","browser":{"connected":true},"uptime":42.1,"sessions":2}

# Ask ChatGPT (text or image prompt)
curl -X POST http://localhost:3333/api/ask \
  -H "Content-Type: application/json" \
  -d '{"provider": "chatgpt", "prompt": "Draw a book cover for a lithium battery report, blue theme, minimalist"}'

# Manage sessions
curl http://localhost:3333/api/sessions
curl -X POST http://localhost:3333/api/sessions -d '{"provider":"chatgpt"}'
```

### Provider Support
| Provider | ID | Status |
|----------|:--:|:------:|
| ChatGPT | `chatgpt` | ✅ Supported (needs login) |
| Google Gemini | `gemini` | ✅ Supported (needs login) |
| DeepSeek | `deepseek` | ✅ Supported (needs login) |
| xAI Grok | `grok` | ✅ Supported (needs login) |
| Microsoft Copilot | `copilot` / `copilot365` | ✅ Supported |

### Comparison: Playwright Python vs Browser-AI-Bridge
| Aspect | Playwright Python | Browser-AI-Bridge |
|--------|:-----------------:|:-----------------:|
| Setup | Install playwright pip package | npm install + .env config |
| Session management | Manual cookie save/load | Auto-persistent profile (/tmp/chrome_ai_debug) |
| API interface | Script-based | REST API on port 3333 |
| Resource usage | Lower | Higher (Node.js + Chrome) |
| Provider tabs | Manual navigation | Auto-created per provider |
| Best for | One-off scraping/automation | Long-running service/API endpoint |

### Account Reference
- Account: 1351712821@qq.com (ChatGPT free account)
- Saved Chrome profile: `/tmp/chrome_ai_debug/` (needs first login)
- ChatGPT session cookies: currently empty (only Cloudflare cookies present)

## Known Issues

### Free Tier Limitations
- Free ChatGPT accounts have a **daily limit** on DALL·E generations (typically ~5-10 images)
- No access to advanced features like image editing or variable generation
- The account shows "Free" in the UI, with "Upgrade - Get Plus" for unlimited access

### Cloudflare Detection
- Playwright from Chinese datacenter IPs → Cloudflare block
- Playwright from **US VPS** (Vultr LA) → login page loads fine
- If detection gets stricter, try increasing delays between actions

### Session Expiry
- ChatGPT session cookies last ~24h
- After expiry, scripts will redirect to login page
- Solution: check for login page by looking for "Log in" text in page content

## Account Reference

- Account: 1351712821@qq.com (ChatGPT free account, created via email)
- User display name: "keke water"
- Password: stored separately, not for automation use (Google not linked)
- DALL·E OpenAI GPT ID: `g-pmuQfob8d` (the official DALL·E image generator)
