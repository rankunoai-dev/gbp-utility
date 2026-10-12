import asyncio
import urllib.parse
from typing import Any

from playwright.async_api import async_playwright

import config


class BrightDataMapsAdapter:
    def __init__(self, ws_url: str = None):
        self.ws_url = ws_url or config.settings.BRIGHT_DATA_WS_URL

    async def fetch_business_knowledge_graph(self, query: str) -> dict[str, Any]:
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&hl=en"
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(self.ws_url)
            page = await browser.new_page()

            client = await page.context.new_cdp_session(page)
            await page.goto(search_url, timeout=60000)

            # Auto-solve captcha if triggered
            try:
                await client.send("Captcha.waitForSolve", {"detectTimeout": 10000})
            except Exception:
                pass

            await page.wait_for_timeout(3000)

            # Extract Knowledge Graph metadata
            data = await page.evaluate("""() => {
                // Name
                const titleEl = document.querySelector('h2[data-attrid="title"]') || document.querySelector('div[data-attrid="title"]');
                const name = titleEl ? titleEl.innerText.trim() : '';
                
                // Rating & Reviews
                const ratingEl = document.querySelector('span.Aq14fc') || document.querySelector('span[aria-hidden="true"]');
                let rating = 0.0;
                let reviewsCount = 0;
                
                // Look for reviews text e.g. "12 Google reviews"
                const textNodes = Array.from(document.querySelectorAll('span, a')).map(el => el.innerText);
                for (const t of textNodes) {
                    if (t.includes('Google reviews') || t.includes('Google review')) {
                        const match = t.match(/(\\d+)\\s+Google/);
                        if (match) reviewsCount = parseInt(match[1]);
                    }
                }
                
                const ratingMatch = document.body.innerText.match(/(\\d\\.\\d)\\s+★/);
                if (ratingMatch) {
                    rating = parseFloat(ratingMatch[1]);
                }
                
                // Address
                let address = '';
                const addrEl = document.querySelector('span.LrzXr');
                if (addrEl) address = addrEl.innerText.trim();
                
                // Primary Category
                let category = '';
                const subTitleEl = document.querySelector('div[data-attrid="subtitle"]') || document.querySelector('span.YhemCb');
                if (subTitleEl) category = subTitleEl.innerText.trim();
                
                // Check if Services tab exists
                const hasServicesTab = Array.from(document.querySelectorAll('div[role="tab"], button')).some(el => el.innerText.trim() === 'Services');
                
                return {
                    name,
                    rating,
                    reviewsCount,
                    address,
                    category,
                    hasServicesTab
                };
            }""")

            await browser.close()
            return data


if __name__ == "__main__":
    adapter = BrightDataMapsAdapter()
    result = asyncio.run(
        adapter.fetch_business_knowledge_graph("Childtime of Fairport 585 Garnsey Rd Fairport NY")
    )
    print("Extracted KG Data:", result)
