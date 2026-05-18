# Chinese Web Login Modal Patterns

When automating login for Chinese web services (Baidu, Alibaba/千问, etc.) from headless Chrome, the login form is typically inside a **cross-origin iframe** that the browser tool's accessibility tree cannot see. Standard ref-based clicking (`browser_click`) won't work on elements inside these iframes.

## ⚠️ Iframe Visibility: Session-Dependent

Some Chinese login iframes are cross-origin and INVISIBLE to the browser tool (no child elements in snapshot). Others (notably Alibaba/千问's SSO) ARE visible and fully interactable via refs.

**Current observations (2026-05-16):**
- **千问 (qianwen.com)** → ✅ Iframe visible, refs work. The Alibaba account iframe shows phone input, code input, login button, and agree/disagree dialog as clickable refs.
- **百度文库** → ❌ Iframe likely invisible (reported as cross-origin). Must use Playwright Python directly.

When a login iframe is invisible, fall back to QR code login (send screenshot to user) or Playwright Python script.

## Common Pattern

| Service | Login Method | Iframe | Approach |
|---------|-------------|:-----:|----------|
| **百度文库** | Phone + SMS code, QR code, or account/password | Invisible | Use Playwright Python directly or QR code scan |
| **千问 (qianwen.com)** | Phone + SMS code, or QR code | Visible ✅ | `browser_click` refs work inside iframe |
| **ChatGPT** | Email + password, then email verification code | No iframe | Direct ref-based clicking works |

## Workarounds When Login Modal Is in Cross-Origin Iframe

### 1. Use Playwright Python directly

Write a standalone Python script with Playwright. The pip-installed `playwright` package can access iframe content directly:

```python
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = await browser.new_page()
        await page.goto('https://wenku.baidu.com/', wait_until='networkidle')
        
        # Access all frames
        for frame in page.frames:
            sms_tab = frame.locator('text=短信登录').first
            if await sms_tab.is_visible(timeout=2000):
                await sms_tab.click()
                await asyncio.sleep(1)
                phone_input = frame.locator('input[type="text"]').first
                await phone_input.fill('138...')
                code_btn = frame.locator('text=获取验证码').first
                await code_btn.click()

asyncio.run(main())
```

### 2. Use `browser_console` + JS evaluation

Execute JavaScript in the main page context to find and interact with elements:

```js
// Find all iframes and search their content
document.querySelectorAll('iframe').forEach(f => {
  try {
    const doc = f.contentDocument || f.contentWindow?.document;
    if (doc) {
      const smsTab = doc.querySelector('[class*="pass-tab"]:nth-child(2)');
      if (smsTab) smsTab.click();
    }
  } catch(e) {}
});
```

### 3. Use `browser_vision` for coordinate-based clicking

The vision tool can see the login modal visually (even in iframes). Use `browser_vision(annotate=true)` to get element coordinates, then use pixel-relative clicking.

### QR Code Login (Best for Chinese Services)

Most Chinese services (Baidu, Alibaba, WeChat) support **QR code login via their mobile app**. This avoids SMS verification entirely:

1. Navigate to the login page
2. Click to show the QR code login option (usually shows by default)
3. Take a screenshot of the QR code
4. Send it to the user via WeChat
5. User scans with their phone app
6. Login completes automatically

#### ⚠️ QR Code: App-Specific (Not Generic)
#### ⚠️ QR Code: App-Specific (Not Generic)
The QR code displayed on **千问 (qianwen.com)** is **APP-specific** — it must be scanned with the **千问APP** on mobile. It will NOT work with WeChat, Alipay, or generic QR code scanners.

- **Confirmed (2026-05-16)**: Scanning with non-千问 apps (e.g., 12306 train app, which shares Alibaba SSO) shows a login confirmation page but with the message **"扫码功能准备中，请通过左侧输入框完成登录"** — the login cannot be completed through non-千问 apps.
- **Baidu** QR codes similarly require the **百度App** specifically — not generic scanners.
- If the user doesn't have the 千问APP installed, this QR code method is not viable
- **Alternative**: SMS verification code (if not rate-limited), or try Taobao/Alipay sign-in links
- **Important**: Once the QR code appears, **do NOT navigate away or reload** the page — doing so invalidates the QR code session. The page must remain open in the same session for the scan callback to work.

#### ⚠️ Taobao/Alipay Links Redirect to about:blank in Headless Mode

The "sign with taobao" and "sign with alipay" links at the bottom of the 千问 login iframe will redirect the page to `about:blank` when clicked in headless Chrome. This is likely due to the OAuth redirect requiring a parent window interaction that headless mode cannot provide.

**If the user wants to use Taobao/Alipay to log in:**
- This requires a real browser window, not headless
- Fall back to QR code (if user has 千问APP) or SMS verification

## SMS Verification Flow (千问/qianwen.com — Confirmed Working)

Complete login flow (verified 2026-05-16):

### ⚠️ Critical: Two-Phase Flow

The 千问 SMS login has a **two-phase authorization flow** where the "同意" dialog appears at TWO different points:

**Phase 1 — Send Code**
1. Navigate to `https://www.qianwen.com/`
2. Click the **"登录"** button in the top-right (ref=e10 or e13)
3. Login iframe appears — phone field visible (ref=e42)
4. Type phone number: `browser_type(ref=e42, text="139...")`
5. Click **"获取验证码"** (ref=e44 or e46)
   → **Confirmation dialog appears** with 用户协议/隐私协议 (ref=e42=不同意, ref=e43=同意)
6. Click **"同意"** (ref=e43) to authorize — **NOW** the SMS is actually sent
   → Button shows "59秒后重发"

**Phase 2 — Enter Code & Login**
7. **Wait for user** to read SMS and send the code via chat
8. Type code: `browser_type(ref=e43 or e45, text="123456")` (⚠️ ref ID may differ from step 6)
9. Click **"登录"** button (ref=e41)
   → **Another confirmation dialog** may appear again
10. Click **"同意"** (ref=e43) if dialog appears again
11. ✅ Login complete — user avatar appears in top-right corner

### ⚠️ SMS Rate Limiting Pitfall

千问 has a strict SMS rate limit: **"获取次数已达上限，请15分钟后再试"**. This is triggered by:
- Reloading the page and re-requesting a code multiple times
- Each page reload creates a new session, but the phone-number-level rate limit persists
- The limit applies PER PHONE NUMBER, not per session/page load
- **Solution**: Avoid page reloads during the login flow. If something goes wrong, work within the existing iframe rather than reloading the whole page.
- **Recovery from limit**: Must wait ~15 minutes before the phone number can receive another code

### ⚠️ Page Reload Invalidates Pending Codes

- Reloading www.qianwen.com clears the login iframe entirely
- Any previously-sent SMS code becomes unusable (system shows "请先发送短信验证码")
- The code is NOT linkable to a new page session
- **Best practice**: Once you start the login flow, don't reload until complete

## SMS Verification Flow (General)

1. Click "短信登录" tab (switch from account login)
2. Enter phone number (`page.fill` or user provides it)
3. Click "获取验证码" button
4. **Wait for user to read the SMS code**
5. User sends the code in chat
6. Enter the code and submit

**Important:** The SMS code arrives on the user's phone, not the server. The user must be available to read it.

## Baidu (百度文库) Login Flow — passport.baidu.com

Baidu's login system is hosted on `passport.baidu.com` and has a different structure from Alibaba/千问:

### Login Page Structure
- Navigate to `https://passport.baidu.com/v2/?login&tpl=wk&u=https://wenku.baidu.com/` for the standalone login page
- Default view shows **QR code login** (scan with Baidu App)
- Click "用户名登录" link to switch to account/password mode

### Account/Password Login
1. Navigate to passport.baidu.com login URL
2. Click "用户名登录" (ref=e2) to switch to credential login mode
3. Enter phone/username in textbox (ref=e4): `browser_type(ref=e4, text="139...")`
4. Enter password in textbox (ref=e5): `browser_type(ref=e5, text="your_password")`
5. Click "登录" button (ref=e6)

### ⚠️ Additional SMS Verification (Security Feature)
After correct credentials, Baidu may require **additional SMS verification** (security 2FA):
- A popup appears: "验证方式选择" with buttons "其他验证" and "去验证"
- Click "去验证" (ref=e6) to send an SMS code to the registered phone
- SMS code input field appears: textbox "6位数验证码" (ref=e5)
- 59-second resend timer on button (ref=e6)
- Also has "换个验证方式" link (ref=e4) for alternative methods

### QR Code Login
- Navigate to passport.baidu.com
- QR code is shown by default on the left side with text "请使用百度App扫码登录"
- User scans with Baidu App on phone
- **Note**: Unlike 千问, the Baidu QR code requires the **百度App**, not just any scanner

## Baidu Wenku AI PPT Workflow (Full)

After logging into 百度文库, you can generate AI PPTs through the smart assistant. The workflow (verified 2026-05-16):

### Step 1: Access the Smart Assistant
1. From Baidu Wenku homepage, click "登录" button → login with credentials/SMS
2. After login, the top-right shows "会员中心" instead of "登录"
3. Click **"智能助手"** in the left sidebar menu, or click one of the AI feature buttons (e.g., "AI帮我写PPT")

### Step 2: Switch to 智能PPT Mode
1. In the smart assistant interface, there are tab buttons at the bottom: **"对话"**, **"智能PPT"**, **"智能写作"**, etc.
2. Click **"智能PPT"** tab to switch to PPT generation mode
3. The interface changes to show: input area for theme, "输入主题生成" button, and layout options

### Step 3: Input Theme & Generate Outline
1. The input area uses a **nested contenteditable div** (not a standard textarea)
2. Type your prompt (e.g., "帮我写一篇PPT，主题为...")
3. **Submit the prompt** — either press Enter (`browser_press`) or click the send arrow button (varies)
4. The AI will generate a complete PPT outline (takes 10-30 seconds)

### Step 4: Review and Edit Outline
- The generated outline shows as editable text boxes for each chapter/section
- Example structure: 标题 → 第1章/1.1/1.2/1.3 → 第2章/2.1/2.2... etc.
- You can click any section to edit its content and title directly

### Step 5: Select Template & Generate Final PPT
1. Scroll to the bottom of the outline page
2. Click the green **"生成PPT"** button (text content: 生成PPT)
3. A template selection panel appears with options:
   - "全部风格", "全部场景", "全部颜色" filter tabs
   - Template thumbnails (教育类通用模板, 企业商务, etc.)
4. Click **"继续生成"** (green button at bottom-right)
5. Wait for the AI to render the complete PPT (may take 30-60 seconds)

### Step 6: Download
- After generation, look for a download button (下载) in the toolbar
- Format options usually include: PPTX, PDF, or PNG images
- Free accounts may have download limitations

### Key Observations
- **Outline quality**: The AI generates surprisingly detailed and relevant outlines. For example, a prompt about "小墨墨渊Flux成长手记" produced 6 chapters with 18 subsections covering birth, capability evolution, key events, tech architecture, relationships, and future outlook.
- **No login needed for outline**: The outline generation step works without being logged in
- **Login needed for download**: You must be logged in to download the final PPT file
- **Template selection requires login**: The template panel and "继续生成" button appear after clicking "生成PPT" — this step happens after login

### ⚠️ Key Differences from 千问 Login

| Feature | 千问 (qianwen.com) | 百度 (passport.baidu.com) |
|---------|-------------------|--------------------------|
| Login modal | Visible iframe ✅ | Standalone page (no iframe issue) |
| QR code app | 千问APP | 百度App |
| SMS rate limit | Strict ("15分钟后重试") | Unknown (likely also limited) |
| Account+password | Not available (SMS/QR only) | Available ✅ |
| 2FA after password | No | Yes (SMS verification required) |

#### Baidu Wenku Homepage vs Standalone Login — Different Behavior

There are TWO ways to log in to Baidu Wenku, with different iframe behaviors:

| Method | URL | Iframe | Interactable |
|--------|-----|:------:|:------------:|
| **Homepage login** | `https://wenku.baidu.com/` → click "登录" | Cross-origin (passport.baidu.com iframe) | ❌ Cannot access elements directly |
| **Standalone passport** | `https://passport.baidu.com/v2/?login&tpl=wk&u=https://wenku.baidu.com/` | No iframe (direct page) | ✅ Full element access via refs |

**Homepage login flow** (cross-origin iframe):
- The login modal is an iframe loading content from `passport.baidu.com`
- `browser_snapshot` shows only a single Iframe element (ref=e1) with no children
- `browser_console` JS evaluation fails with `SecurityError: Blocked a frame with origin` — cross-origin restriction
- **Workaround**: Use `browser_vision(annotate=true)` to identify tab positions visually, then use `document.elementFromPoint(x, y)` in `browser_console` to find and click elements in the parent page's DOM
- Example: Find "短信登录" tab span by scanning all `span.switch-item` elements in the login container via `document.elementFromPoint(777, 145)`
- However, even when you successfully click tabs, the iframe content may cause the page to go blank (reported 2026-05-16)

**Standalone passport login flow** (no iframe):
- Navigate to passport.baidu.com directly → full page, all elements visible in accessibility tree
- Can use standard `browser_click(ref)` and `browser_type(ref, text)` calls
- Account/password mode available after clicking "用户名登录"
- After successful login, browser redirects back to Wenku

**Strategic decision for Chinese AI PPT platforms**:
Both 千问 and 百度文库 have strong anti-automation measures. Keke confirmed "估计和千问一样" — they're the same class of problem. The reliable path is:
1. Generate content locally (markdown, python-pptx)
2. Deliver as file to user
3. Let user paste into any PPT tool they prefer
This avoids burning login quotas, triggering anti-bot escalation, and wasting time on fragile automation.

### ⚠️ Context Compaction Resets Browser Sessions

**Critical limitation**: When the conversation undergoes context compaction (long sessions), the **entire browser state resets** — cookies, login sessions, navigation history, and any open pages are all lost. This means:

- All previous login sessions (百度, 千问, etc.) become invalid
- Must re-navigate to the target URL from scratch
- Must re-authenticate (re-enter credentials)
- Any pending flows (generated PPTs, downloaded files) are lost in the browser — always download/save files before compaction
- **Mitigation**: Before context compaction is imminent (session is getting long), save all important data to disk, complete any pending downloads, and inform the user that browser state will reset

### App-Specific Authentication on Chinese Services

Multiple Chinese services require their specific mobile app for authentication:

| Service | Required App | Notes |
|---------|:-----------:|-------|
| 千问 (qianwen.com) | 千问APP | QR + 12306/Alipay won't work |
| 百度文库/百度系 | 百度App | QR code requires Baidu App specifically |
| Taobao/Alipay SSO | Alipay or Taobao App | OAuth redirect doesn't work in headless |

**Rule of thumb**: If a Chinese service shows a QR code for login, ask the user if they have the specific app installed before proceeding. If they don't, fall back to SMS verification or account/password (if available) — but be aware of rate limits on SMS sends.

### Summary: When to Abandon Automated Login

If you encounter any of these signs, **consider generating content locally** instead of fighting the platform:
1. Cross-origin iframe (can't access elements via refs or JS)
2. Repeated SMS rate limits ("获取次数已达上限")
3. QR code requires app user doesn't have
4. Page goes blank after interacting with iframe elements
5. Captcha escalation (slider → image select → puzzle) on repeated attempts
6. Multiple different services (千问 → 百度 → others) all have similar issues

The local generation approach (markdown content → file delivery) bypasses ALL these issues and is almost always faster.

## Common Pitfalls for Both Services

1. **Rate limiting across services** — Hitting rate limits on one service (e.g., 千问 SMS limit) does NOT affect the other (Baidu), but both have their own limits. If one approach is blocked, try the other service.

2. **Page reloads reset everything** — Reloading or navigating away during login invalidates pending codes and resets the flow. Complete the flow in one shot.

3. **Multiple code sends cause confusion** — Each new SMS send invalidates the previous code. If the user sends multiple codes, use the LAST one received. Best practice: send a single SMS and wait for user input.

4. **User security concern** — The user expressed "别试千问了，又要被封" (don't try 千问 anymore, it'll get blocked). Repeated login attempts at high frequency can trigger security blocks. If a service rejects 2-3 login attempts, **switch to a different service or method** rather than retrying. This was demonstrated successfully: 千问 SMS limit → swiped to Baidu login → succeeded on first attempt.

5. **QR code sessions are fragile** — The QR code session is tied to the current browser page. If you navigate away, reload, or send the user an outdated screenshot, the QR code becomes invalid and the scan won't work. Take the screenshot and send it immediately while keeping the page untouched.

6. **Contenteditable divs in Chinese UIs** — Baidu Wenku's AI assistant uses nested `contenteditable` divs instead of standard `<input>` or `<textarea>` elements. These behave differently:
   - `browser_type` may append text instead of replacing content
   - The placeholder text may not clear automatically
   - Pressing Enter may not submit; you may need to find and click a separate send button
   - **Workaround**: If `browser_type` doesn't work as expected, use `browser_click` on the inner editable element first to focus it, then type. For submit, try both Enter key (`browser_press`) and clicking visible send/generate buttons nearby.

## 千问 AI PPT Workflow

千问 (qianwen.com) has a free AI PPT generation feature. Key workflow:

### Generation (No Login Required)
1. Navigate to `https://tongyi.aliyun.com/qianwen/` (redirects to `https://www.qianwen.com/`)
2. Click **"PPT创作"** button (specialized UI opens with "万物皆可PPT" header)
3. Enter prompt text describing content outline + style preferences
4. Click send — AI generates ~30-60 seconds, output ~2.87MB
5. Edit inline: text, images, shapes, colors, template switching available
6. Templates: 热门模板, 课堂教育, 科研论文, 工作汇报

### Download (Login Required)
1. Click **下载 → 下载PPT** (or 下载PDF / 下载长图)
2. Login modal appears (cross-origin iframe)
3. Use SMS verification or QR code (千问APP scan)
4. After login, download proceeds

### Login Modal Details (verified 2026-05-16)
- Inside an iframe (visible in browser_snapshot with child refs)
- SMS tab auto-shown with: phone input, code input, and 获取验证码 button
- After clicking 登录, a confirmation dialog appears: 同意 (ref=e43 typically) / 不同意
- Phone format: +86 prefix by default, enter 11-digit Chinese number
- After login, page session persists — user avatar appears in top bar
- **Trick**: The browser tool CAN interact directly with iframe elements on this site. Use `browser_type` on refs to fill phone and code, then `browser_click` on the login button. No need for Playwright Python or JS eval workarounds.

## Alibaba/千问 vs Baidu/Paddle Login Differences

- **Cross-origin iframe restriction**: `browser_snapshot` and `browser_click` refs cannot see into cross-origin iframes. Login modals appear as a single Iframe element with no children in the accessibility tree.
- **Playwright pip package dependency**: Playwright Python must be installed separately (`pip install playwright`). The npm-installed Playwright (used by the agent-browser tool) cannot be imported from Python.
- **Browser session reset**: Long-running browser sessions may timeout or get blank pages when switching between targets (e.g., going from Baidu to 千问). Navigate fresh to each target.
