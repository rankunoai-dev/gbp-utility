import urllib.request
import re
from bs4 import BeautifulSoup

urls = {
    'fairport': 'https://www.childtime.com/your-local-school/fairport-ny-0002/',
    'henrietta': 'https://www.childtime.com/your-local-school/rochester-ny-0003/'
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

for name, u in urls.items():
    print(f'Fetching {name}: {u}')
    req = urllib.request.Request(u, headers=headers)
    html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    
    # Address extraction
    addr_block = soup.find('div', class_=re.compile(r'address', re.I))
    if addr_block:
        print('  Address block text:', repr(addr_block.get_text(separator=' ', strip=True)))
        
    # Phone
    phone = soup.find('a', href=re.compile(r'^tel:'))
    if phone:
        print('  Phone:', phone.get_text(strip=True))
        
    # Programs from links
    prog_links = soup.find_all('a', href=re.compile(r'/educational-programs/'))
    programs = list(set([p.get_text(strip=True) for p in prog_links if p.get_text(strip=True)]))
    print('  Educational Programs:', programs)
    print('-'*50)
