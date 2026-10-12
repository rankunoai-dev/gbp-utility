import asyncio
from playwright.async_api import async_playwright

BROWSER_WS = "wss://brd-customer-hl_36e868a7-zone-gbp_browser_api:gp2tc3xdyzcz@brd.superproxy.io:9222"
SEARCH_URL = "https://www.google.com/search?q=Childtime+of+Fairport+585+Garnsey+Rd+Fairport+NY&hl=en"

async def test_unlock():
    print("[*] Connecting to Scraping Browser with auto-solver...")
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(BROWSER_WS)
        page = await browser.new_page()
        
        # In Bright Data, client creates a session that auto-solves captchas
        client = await page.context.new_cdp_session(page)
        
        print(f"[*] Navigating to {SEARCH_URL}...")
        await page.goto(SEARCH_URL, timeout=60000)
        
        # Give Bright Data's CAPTCHA solver a few seconds if prompted
        print("[*] Waiting 6 seconds for any challenge resolution...")
        await page.wait_for_timeout(6000)
        
        title = await page.title()
        print(f"[+] Loaded title: {title}")
        
        await page.screenshot(path="search_resolved.png")
        print("[+] Screenshot saved to search_resolved.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_unlock())
