import asyncio
import urllib.parse
from playwright.async_api import async_playwright

BROWSER_WS = "wss://brd-customer-hl_36e868a7-zone-gbp_browser_api:gp2tc3xdyzcz@brd.superproxy.io:9222"

QUERY = "Childtime of Fairport 585 Garnsey Rd Fairport NY"
SEARCH_URL = f"https://www.google.com/search?q={urllib.parse.quote(QUERY)}&hl=en"

async def test_search():
    print(f"[*] Navigating to Google Search Place View: {SEARCH_URL}")
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(BROWSER_WS)
        page = await browser.new_page()
        
        await page.goto(SEARCH_URL, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(4000)
        
        title = await page.title()
        print(f"[+] Loaded title: {title}")
        
        await page.screenshot(path="bright_data_search_kg.png")
        print("[+] Saved screenshot: bright_data_search_kg.png")
        
        html = await page.content()
        with open("search_kg.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        # Check for categories in knowledge graph
        cats = ["Day care center", "Preschool", "Child care agency", "Nursery school", "After school program", "Summer camp organizer"]
        found = [c for c in cats if c in html]
        print(f"[+] Categories found in Search Knowledge Graph: {found}")
        
        # Look for Services button / tab
        services_btn = await page.query_selector('text="Services"')
        print(f"[+] 'Services' element found: {services_btn is not None}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_search())
