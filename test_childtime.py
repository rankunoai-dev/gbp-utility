import urllib.request
import re
from bs4 import BeautifulSoup

urls = [
    'https://www.childtime.com/your-local-school/fairport-ny-0002/',
    'https://www.childtime.com/your-local-school/rochester-ny-0003/'
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

for u in urls:
    req = urllib.request.Request(u, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.title.string if soup.title else ''
            print(f'URL: {u}')
            print(f'Title: {title}')
            # Look for address
            addr = soup.find(class_=re.compile(r'address', re.I))
            if addr:
                print('Address snippet:', addr.get_text(strip=True)[:150])
            # Find program / services links
            programs = [a.get_text(strip=True) for a in soup.find_all('a', href=re.compile(r'/educational-programs/'))]
            print('Programs found:', list(set(programs))[:10])
            print('-'*50)
    except Exception as e:
        print(f'Error fetching {u}: {e}')
