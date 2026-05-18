# Vultr Login Automation Pattern

Use Playwright Python on a Singapore VPS (via SSH) to automate Vultr login and obtain API credentials.

## URL

- Login page: `https://my.vultr.com` (redirects to `https://console.vultr.com/`)
- API settings: `https://my.vultr.com/settings/setup/`

## Complete Login Script

```python
import asyncio
from playwright.async_api import async_playwright

CHROME_PATH = '/root/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
        )
        page = await browser.new_page()

        await page.goto('https://my.vultr.com', timeout=60000, wait_until='domcontentloaded')
        await asyncio.sleep(3)

        # Dismiss consent banner (Ketch/lanyard overlay)
        btn = page.locator('button:has-text("I Understand")')
        if await btn.count() > 0:
            await btn.click()
            await asyncio.sleep(1)

        # Fill credentials
        await page.fill('input[name="username"]', '<email>')
        await page.fill('input[name="password"]', '<password>')

        # Submit via JS to bypass overlay interception
        await page.evaluate("""
            document.querySelector('button[type="submit"]').click()
        """)
        await asyncio.sleep(5)

        print(f'URL: {page.url}')
        print(f'Title: {await page.title()}')

        # Save cookies for API reuse
        cookies = await page.context.cookies()
        cookie_str = '; '.join([f'{c["name"]}={c["value"]}' for c in cookies])
        with open('/tmp/vultr_cookies.txt', 'w') as f:
            f.write(cookie_str)

        await browser.close()

asyncio.run(main())
```

## Expected Behavior

1. Login redirects to `https://console.vultr.com/` with title "Log In to your Vultr Account - Vultr.com"
2. After successful credential entry and submission, title changes to "Authenticate - Vultr.com"
3. **2FA/Email verification is required** — a verification code is sent to the account email
4. After 2FA bypass, cookies include `PHPSESSID` and `auth_browser` which enable API access

## Cookies After Login

Key cookies for API access:
- `PHPSESSID`: PHP session ID
- `auth_browser`: Browser authentication token
- `last_login_username`: Email used for login

Use with curl: `curl --cookie /tmp/vultr_cookies.txt https://api.vultr.com/v2/...`

## Running from Main Server

Write the script locally, scp it to the VPS, then execute via SSH:

```bash
scp /tmp/vultr_login.py root@45.76.185.1:/tmp/vultr_login.py
ssh root@45.76.185.1 "python3 /tmp/vultr_login.py"
```

## Notes

- Vultr's login flow requires email verification (2FA) after password — the user must provide the code
- The API key can be retrieved from the settings page after full authentication
- Vultr's Cloudflare challenge is lightweight from Singapore IPs — headless Playwright passes without issue
- The consent banner (Ketch privacy platform) intercepts pointer events — always use evaluate() for clicks
