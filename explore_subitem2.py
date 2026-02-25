import re
import sys
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')

with open('inner.html', encoding='utf-8') as f:
    inner_html = f.read()
inner_soup = BeautifulSoup(inner_html, 'html.parser')

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

count = 0
for grp in inner_soup.find_all('div', class_='schedule__group'):
    items_div = grp.find('div', class_='schedule__group-item-items')
    if not items_div:
        continue
    items = items_div.find_all('div', class_='schedule__group-item-item')
    if not items:
        continue
    
    desc = grp.find('div', class_='schedule__group-item-description')
    h1 = desc.find('h1') if desc else None
    session_title = clean_text(h1.get_text()) if h1 else '?'
    
    time_div = grp.find('div', class_='schedule__group-time')
    spans = time_div.find_all('span') if time_div else []
    start = spans[0].get_text(strip=True) if spans else '?'
    end = spans[1].get_text(strip=True) if len(spans) > 1 else '?'
    
    print(f"\n=== {session_title} [{start}-{end}] ===")
    for i, item in enumerate(items):
        h1_item = item.find('h1')
        title = clean_text(h1_item.get_text()) if h1_item else '?'
        print(f"  Item {i+1}: {title[:80]}")
        for p in item.find_all('p'):
            strong = p.find('strong')
            label = clean_text(strong.get_text()) if strong else ''
            txt = clean_text(p.get_text())
            print(f"    [{label}] {txt[:120]}")
    
    count += 1
    if count >= 5:
        break
