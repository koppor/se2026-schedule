import sys
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')
with open('inner.html', encoding='utf-8') as f:
    inner_html = f.read()
inner_soup = BeautifulSoup(inner_html, 'html.parser')

for grp in inner_soup.find_all('div', class_='schedule__group'):
    desc = grp.find('div', class_='schedule__group-item-description')
    if desc:
        h1 = desc.find('h1')
        if h1 and 'Engineering Intelligent Systems' in h1.get_text():
            print('=== FULL GROUP HTML ===')
            print(str(grp)[:10000])
            break

print("\n\n=== Sustainability and Reliability ===")
for grp in inner_soup.find_all('div', class_='schedule__group'):
    desc = grp.find('div', class_='schedule__group-item-description')
    if desc:
        h1 = desc.find('h1')
        if h1 and 'Sustainability and Reliability' in h1.get_text():
            print(str(grp)[:10000])
            break
