import urllib.request
import re
import json

url = 'https://www.google.com/maps/place/Childtime+of+Fairport/@43.0886534,-77.4526553,17z/data=!3m1!4b1!4m6!3m5!1s0x89d6cbe9aa13c1cf:0xd97f0a8276f7f2b1!8m2!3d43.0886534!4d-77.4526553!16s%2Fg%2F1tf76m2w?entry=ttu'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}
req = urllib.request.Request(url, headers=headers)
try:
    html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
    print('Fetched maps page successfully, length:', len(html))
    target_cats = ['Day care center', 'Preschool', 'Child care agency', 'Nursery school', 'After school program', 'Summer camp organizer', 'Learning center', 'Youth care service']
    found = [cat for cat in target_cats if cat in html]
    print('Found categories in raw page:', found)
except Exception as e:
    print('Error:', e)
