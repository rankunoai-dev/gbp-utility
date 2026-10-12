import urllib.request
import re

url = 'https://www.google.com/search?q=Childtime+of+Fairport+585+Garnsey+Rd+Fairport+NY+14450&hl=en'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}
req = urllib.request.Request(url, headers=headers)
try:
    html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
    print('Search HTML length:', len(html))
    target_cats = ['Day care center', 'Preschool', 'Child care agency', 'Nursery school', 'After school program', 'Summer camp organizer', 'Learning center', 'Youth care service']
    found = [cat for cat in target_cats if cat in html]
    print('Found in Google Search HTML:', found)
except Exception as e:
    print('Error:', e)
