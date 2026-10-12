import asyncio
import json
import re
from playwright.async_api import async_playwright

BROWSER_WS = "wss://brd-customer-hl_36e868a7-zone-gbp_browser_api:gp2tc3xdyzcz@brd.superproxy.io:9222"

TARGET_URL = "https://www.google.com/maps/place/Childtime+of+Fairport/@43.0886534,-77.4526553,17z/data=!3m1!4b1!4m6!3m5!1s0x89d6cbe9aa13c1cf:0xd97f0a8276f7f2b1!8m2!3d43.0886534!4d-77.4526553!16s%2Fg%2F1tf76m2w?entry=ttu"

async def inspect_place_data():
    print(f"[*] Connecting to Bright Data browser to inspect: {TARGET_URL}")
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(BROWSER_WS)
        page = await browser.new_page()
        
        # Navigate to Google Maps place page
        await page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
        title = await page.title()
        print(f"[+] Loaded title: {title}")
        
        # Evaluate page to find business categories in window state
        # In Google Maps, the app state holds full metadata
        data_script = await page.evaluate('''() => {
            // Find category elements in the DOM
            const primaryCatBtn = document.querySelector('button[jsaction*="category"]');
            const primaryCat = primaryCatBtn ? primaryCatBtn.innerText : '';
            
            // Search window for category arrays
            const pageHtml = document.documentElement.innerHTML;
            return {
                primaryCat: primaryCat,
                htmlLength: pageHtml.length
            };
        }''')
        print(f"[+] Primary category found in DOM: {data_script['primaryCat']}")
        
        # Save page content to search for categories
        content = await page.content()
        with open("fairport_maps_rendered.html", "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[+] Saved rendered HTML ({len(content)} bytes) to fairport_maps_rendered.html")
        
        # Check for known categories in rendered DOM
        known_cats = [
            "Day care center", "Preschool", "Child care agency", 
            "Nursery school", "After school program", "Summer camp organizer", 
            "Learning center", "Youth care service", "Language school"
        ]
        found = [c for c in known_cats if c in content]
        print(f"[+] Categories detected in rendered HTML: {found}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_place_data())
