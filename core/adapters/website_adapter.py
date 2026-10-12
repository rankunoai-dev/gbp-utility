import urllib.request
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any

class WebsiteAdapter:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def scrape_school_page(self, url: str) -> Dict[str, Any]:
        req = urllib.request.Request(url, headers=self.headers)
        html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')
        
        # 1. Address
        street = ''
        city_state_zip = ''
        street_el = soup.find(class_=re.compile(r'street', re.I))
        if street_el:
            street = street_el.get_text(strip=True)
        city_el = soup.find(class_=re.compile(r'cityState', re.I))
        if city_el:
            city_state_zip = city_el.get_text(strip=True)
            
        full_address = f'{street}, {city_state_zip}'.strip(', ')
        
        # 2. Programs offered
        prog_links = soup.find_all('a', href=re.compile(r'/educational-programs/'))
        raw_programs = [p.get_text(strip=True) for p in prog_links if p.get_text(strip=True)]
        
        # Filter navigation fluff like 'Our Programs', empty strings
        programs = []
        for p in set(raw_programs):
            if p.lower() not in ['our programs', 'learn more', 'programs', '']:
                programs.append(p)
                
        # 3. Phone
        phone = ''
        phone_el = soup.find('a', href=re.compile(r'^tel:'))
        if phone_el:
            phone = phone_el.get_text(strip=True)
            
        return {
            'url': url,
            'address': full_address,
            'phone': phone,
            'programs': sorted(programs)
        }

if __name__ == '__main__':
    adapter = WebsiteAdapter()
    data = adapter.scrape_school_page('https://www.childtime.com/your-local-school/fairport-ny-0002/')
    print('Scraped Fairport Programs:', data['programs'])
