import asyncio
from playwright.async_api import async_playwright

BROWSER_WS = "wss://brd-customer-hl_36e868a7-zone-gbp_browser_api:gp2tc3xdyzcz@brd.superproxy.io:9222"
SEARCH_URL = "https://www.google.com/search?q=Childtime+of+Fairport+585+Garnsey+Rd+Fairport+NY&hl=en"

async def test_solve():
    print("[*] Connecting to Scraping Browser...")
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(BROWSER_WS)
        page = await browser.new_page()
        
        # Connect to CDP session to trigger Bright Data's captcha solver
        client = await page.context.new_cdp_session(page)
        
        print(f"[*] Navigating to {SEARCH_URL}...")
        await page.goto(SEARCH_URL, timeout=60000)
        
        print("[*] Calling Captcha.waitForSolve via CDP...")
        try:
            # Bright Data provides a CDP command 'Captcha.solve' or 'Captcha.waitForSolve'
            result = await client.send('Captcha.waitForSolve', {'detectTimeout': 15000})
            print(f"[+] Captcha solver result: {result}")
        except Exception as e:
            print(f"[!] Captcha solver command error: {e}")
            
        await page.wait_for_timeout(5000)
        title = await page.title()
        print(f"[+] Current title: {title}")
        
        await page.screenshot(path="search_solved.png")
        print("[+] Screenshot saved to search_solved.png")
        
        # Check if real search results or KG loaded
        content = await page.content()
        cats = ["Day care center", "Preschool", "Child care agency", "Nursery school"]
        found = [c for c in cats if c in content]
        print(f"[+] Categories found: {found}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_solve())
