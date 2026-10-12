import asyncio
import json
import re
from playwright.async_api import async_playwright

BROWSER_WS = "wss://brd-customer-hl_36e868a7-zone-gbp_browser_api:gp2tc3xdyzcz@brd.superproxy.io:9222"
TARGET_URL = "https://www.google.com/maps/place/Childtime+of+Fairport/@43.0886534,-77.4526553,17z/data=!3m1!4b1!4m6!3m5!1s0x89d6cbe9aa13c1cf:0xd97f0a8276f7f2b1!8m2!3d43.0886534!4d-77.4526553!16s%2Fg%2F1tf76m2w?entry=ttu"

async def test_fast_load():
    print("[*] Connecting to Bright Data browser...")
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(BROWSER_WS)
        page = await browser.new_page()
        
        print(f"[*] Navigating with domcontentloaded: {TARGET_URL}")
        # Use domcontentloaded instead of networkidle
        await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=45000)
        print("[+] DOMContentLoaded fired! Waiting 5s for JS render...")
        await page.wait_for_timeout(5000)
        
        title = await page.title()
        print(f"[+] Page Title: {title}")
        
        # Take a screenshot to inspect
        await page.screenshot(path="bright_data_fairport.png")
        print("[+] Saved screenshot: bright_data_fairport.png")
        
        # Check primary category text
        cat_text = await page.evaluate('''() => {
            const btn = document.querySelector('button[jsaction*="category"]');
            return btn ? btn.innerText.trim() : 'NOT_FOUND';
        }''')
        print(f"[+] Extracted Primary Category button: {cat_text}")
        
        # Extract HTML to check for secondary categories in page data
        html = await page.content()
        with open("bright_data_fairport.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[+] Saved {len(html)} bytes of HTML")
        
        # Check for categories in the HTML
        known_cats = [
            "Day care center", "Preschool", "Child care agency", 
            "Nursery school", "After school program", "Summer camp organizer", 
            "Learning center", "Youth care service"
        ]
        found = [c for c in known_cats if c in html]
        print(f"[+] Categories found in rendered HTML: {found}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_fast_load())
