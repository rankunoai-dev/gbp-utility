import asyncio
import os
from playwright.async_api import async_playwright

BROWSER_WS = "wss://brd-customer-hl_36e868a7-zone-gbp_browser_api:gp2tc3xdyzcz@brd.superproxy.io:9222"

async def test_connection():
    print("[*] Connecting to Bright Data Scraping Browser via CDP...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(BROWSER_WS)
            print("[+] Successfully connected to Bright Data remote Chromium!")
            page = await browser.new_page()
            
            test_url = "https://www.google.com"
            print(f"[*] Navigating to {test_url}...")
            await page.goto(test_url, timeout=30000)
            title = await page.title()
            print(f"[+] Page loaded! Title: {title}")
            
            await browser.close()
            print("[+] Test completed successfully!")
    except Exception as e:
        print(f"[-] Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
