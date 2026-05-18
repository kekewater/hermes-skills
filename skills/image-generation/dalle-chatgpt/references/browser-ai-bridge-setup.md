# Browser-AI-Bridge Setup (ChatGPT Web REST API)

**browser-ai-bridge** is a local REST API server that drives real Chrome browser sessions to interact with AI web interfaces — ChatGPT, Gemini, DeepSeek, Grok, and Copilot. It provides an alternative to direct Playwright scripting for accessing ChatGPT web, including the GPT-image model for image generation.

**GitHub:** https://github.com/jeffrey-nz/browser-ai-bridge

## When to Use

- Current Playwright-based approach (`generate.py`) fails due to cookie expiry or UI changes
- Need a programmatic REST API to ChatGPT's web interface (including GPT-image)
- Want persistent browser sessions with automatic login state management
- **Alternative to OpenAI API key** — uses web login, no API key needed

## Architecture

```
Your agent → POST /api/ask → browser-ai-bridge (port 3333)
                              └── Playwright CDP → Chrome tab (logged into ChatGPT)
                                      └── Returns AI response text
```

## Installation (China Server)

### Prerequisites

- Node.js >= 20 (server has v22.22.2 ✅)
- Chrome (Playwright's Chrome at `~/.cache/ms-playwright/chromium-1217/chrome-linux64/chrome` ✅)
- Vultr proxy (:8888) for accessing ChatGPT from China

### Step 1: Clone & Install

```bash
# Clone from GitHub (GitHub accessible from China without proxy)
git clone https://github.com/jeffrey-nz/browser-ai-bridge.git
cd browser-ai-bridge

# Install dependencies (use npmmirror for speed in China)
npm install --registry https://registry.npmmirror.com
```

**Note:** `npm install -g browser-ai-bridge` from npm registry is slow through proxy (502 errors from Tencent mirror). Source clone is preferred.

### Step 2: Symlink Chrome

The tool looks for `google-chrome` in PATH. Playwright's Chrome is in a custom path:

```bash
sudo ln -sf /home/ubuntu/.cache/ms-playwright/chromium-1217/chrome-linux64/chrome /usr/local/bin/google-chrome
```

### Step 3: Patch Chrome Args for Proxy

The `args.js` file doesn't include a proxy flag by default. Add `CHROME_PROXY` env var support:

Edit `src/browser/launcher/args.js` — after the args array definition, add:

```javascript
// Proxy support: CHROME_PROXY env var (e.g. http://127.0.0.1:8888)
if (process.env.CHROME_PROXY) {
  args.push(`--proxy-server=${process.env.CHROME_PROXY}`);
}
```

### Step 4: Configure .env

```env
PORT=3333
CHROME_PROXY=http://127.0.0.1:8888
HEADLESS=true
LOG_LEVEL=info
```

`HEADLESS=true` for headless servers. `HEADLESS=offscreen` available for display-equipped servers (avoids anti-bot prompts on Gemini).

### Step 5: First Run — Manual ChatGPT Login

```bash
cd /path/to/browser-ai-bridge
CHROME_PROXY=http://127.0.0.1:8888 HEADLESS=true node src/index.js
```

First run launches a wizard that opens Chrome tabs for each AI provider. Since it's headless, it auto-assumes providers are ready. For actual ChatGPT access, you need to log in once.

**Remote Login via SSH Tunnel (for China server):**

The Chrome instance starts with CDP (Chrome DevTools Protocol) on port 9222. To log into ChatGPT remotely from your local machine:

1. **On the server**, start the bridge normally (wizard completes, server is running)
2. **On your local machine**, create an SSH tunnel:
   ```bash
   ssh -L 9222:127.0.0.1:9222 ubuntu@SERVER_IP
   ```
3. **On your local machine**, open Chrome and go to `chrome://inspect`
4. Click "Configure..." and add `localhost:9222`
5. The server's Chrome instance appears — click "inspect" next to it
6. A DevTools window opens showing the server's Chrome browser
7. Navigate to `https://chatgpt.com/auth/login` within DevTools
8. Log in with your ChatGPT credentials (or Google/Apple SSO)
9. Once logged in, the session is saved to Chrome's user data directory (`/tmp/chrome_ai_debug/`)
10. Subsequent restarts persist the login state

**Alternative:** If DevTools forwarding is impractical, you can:
- Replace the Chrome profile directory with one from a machine that's already logged into ChatGPT
- Or extract cookies from your own ChatGPT session and inject them via DevTools console

**After login is complete:** Verify with:

```bash
curl http://localhost:3333/api/ping
# Expected: {"status":"ready","browser":{"connected":true},...}

curl -X POST http://localhost:3333/api/ask \
  -H "Content-Type: application/json" \
  -d '{"provider":"chatgpt","prompt":"Say hello in one sentence."}'
# Expected: {"success":true,"response":"Hello! ..."}
```

## Running in Background (tmux)

```bash
tmux new-session -d -s bab
tmux send-keys -t bab "cd /path/to/browser-ai-bridge && CHROME_PROXY=http://127.0.0.1:8888 HEADLESS=true node src/index.js > /tmp/bab.log 2>&1" Enter
```

Check logs: `cat /tmp/bab.log`
Kill: `tmux kill-session -t bab`

## Integration with Hermes Agent

### Method 1: Direct curl calls (simplest)

```python
import requests, json
resp = requests.post("http://localhost:3333/api/ask",
    json={"provider": "chatgpt", "prompt": "Your message here"})
result = resp.json()["response"]
```

### Method 2: MCP tool

Configure an MCP server that wraps the browser-ai-bridge API, making it available as a tool in Hermes sessions.

## Session State & Profile Diagnosis

Before starting, you can check if ChatGPT is actually logged in:

```bash
# Check Chrome profile cookies for ChatGPT
python3 -c "
import sqlite3
conn = sqlite3.connect('/tmp/chrome_ai_debug/Default/Cookies')
cur = conn.cursor()
cur.execute(\"SELECT host_key, name, length(value) FROM cookies WHERE host_key LIKE '%openai%' OR host_key LIKE '%chatgpt%'\")
rows = cur.fetchall()
for r in rows:
    print(f'{r[0]} | {r[1]} | len={r[2]}')
conn.close()
"
```

- **Empty/zero-length cookies** (only `cf_chl_rc_ni`, `__cf_bm` with len=0) → **NOT logged in**. Bad Gateway on API calls.
- **Valid session cookies** (non-zero length) → Logged in. Server responds normally.

The saved profile may exist but have no valid ChatGPT/OpenAI session. In that case, the server starts, says "Setup Complete" but returns **Bad Gateway** for all provider requests. This is the expected behavior when no login has been performed.

## Remote Login via SSH Tunnel (for China server)

When profile has no ChatGPT session, Keke needs to log in once remotely:

### Step-by-step

1. **Start Browser-AI-Bridge** (Chrome runs with CDP on port 9222)

2. **On Keke's computer, create an SSH tunnel** (forward CDP port):
   ```bash
   ssh -L 9222:127.0.0.1:9222 ubuntu@SERVER_IP -p PORT
   ```

3. **On Keke's computer, open Chrome** → go to `chrome://inspect` → click "Configure..." → add `localhost:9222`

4. **The server's Chrome appears** — click "inspect" → DevTools window opens showing the server's Chrome

5. **Navigate to** `https://chatgpt.com/auth/login` within DevTools

6. **Log in** with ChatGPT credentials (`1351712821@qq.com`)

7. **Cookies are saved** to `/tmp/chrome_ai_debug/Default/Cookies` automatically

8. **Subsequent restarts** preserve the login state. Verify with:
   ```bash
   curl http://localhost:3333/api/ping
   # → {"status":"ready","browser":{"connected":true}...}
   
   curl -X POST http://localhost:3333/api/ask \
     -H "Content-Type: application/json" \
     -d '{"provider":"chatgpt","prompt":"Say hello"}'
   # → {"success":true,"response":"Hello!..."}
   ```

9. **If it works**, the server is ready. Stop it and restart in background (tmux).

## Limitations & Pitfalls

1. **No standard image output handling** — The API returns response text only. Image generation (GPT-image) output format is unknown. May need custom handling to extract images from the response.
2. **Login state persistence** — ChatGPT sessions expire periodically. The Chrome profile at `/tmp/chrome_ai_debug/` preserves cookies across restarts, but long idle periods may require re-login. Check with the cookie diagnosis command above.
3. **HEADLESS=true + Gemini** — Triggers Google account chooser modal that blocks input. Fine for ChatGPT. Use `HEADLESS=offscreen` for Gemini (requires X display server).
4. **Memory usage** — Each Chrome tab consumes ~200-500MB RAM. The server creates one tab per provider. On 3.6GB server, this is noticeable but manageable.
5. **Proxy dependency** — All provider sites are accessed via Vultr proxy. If the SSH tunnel drops, requests time out. Always check proxy health first.
6. **Provider DOM changes** — The CSS selectors in `src/ai/<provider>/locators.js` break when sites update. Run `npm run audit -- --provider ChatGPT` to detect issues.
