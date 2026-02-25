from bs4 import BeautifulSoup
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('inner.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

tabs = soup.find_all('div', class_='tab')
for tab in tabs:
    radio = tab.find('input', type='radio')
    if not radio:
        continue
    radio_id = radio.get('id', '')
    if 'wednesday' not in radio_id:
        continue

    tab_content = tab.find('div', class_='tab-content')
    if not tab_content:
        continue
    schedule = tab_content.find('div', class_='schedule')
    if not schedule:
        continue

    track_inputs = schedule.find_all('input', type='radio')
    sub_tab_contents = schedule.find_all('div', class_='sub-tab-content', recursive=False)

    for i, (inp, stc) in enumerate(zip(track_inputs, sub_tab_contents)):
        label = schedule.find('label', attrs={'for': inp.get('id', '')})
        track_name = label.get_text(strip=True) if label else inp.get('id', '')
        if 'scientific' not in track_name.lower():
            continue
        
        groups = stc.find_all('div', class_='schedule__group', recursive=False)
        print(f'Scientific Program: {len(groups)} groups total')
        
        for j, grp in enumerate(groups):
            time_div = grp.find('div', class_='schedule__group-time')
            spans = time_div.find_all('span') if time_div else []
            start_time = spans[0].get_text(strip=True) if spans else '?'
            end_time = spans[1].get_text(strip=True) if len(spans) > 1 else '?'
            
            items = grp.find_all('div', class_='schedule__group-item')
            print(f'  Group {j}: {start_time}-{end_time}, {len(items)} item(s)')
            
            for item in items:
                desc = item.find('div', class_='schedule__group-item-description')
                h1 = desc.find('h1') if desc else None
                title_text = h1.get_text(strip=True)[:60] if h1 else '?'
                
                # Find room
                room_text = 'no room'
                if desc:
                    for p in desc.find_all('p'):
                        full = p.get_text(strip=True)
                        if 'Room' in full or 'Location' in full:
                            room_text = full[:50]
                            break
                
                sub_items = item.find('div', class_='schedule__group-item-items')
                n_sub = len(sub_items.find_all('div', class_='schedule__group-item-item')) if sub_items else 0
                print(f'    -> {title_text} | {room_text} | sub_items={n_sub}')
