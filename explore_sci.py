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

    print(f'Wednesday has {len(track_inputs)} sub-tabs, {len(sub_tab_contents)} sub-tab-contents')
    for i, (inp, stc) in enumerate(zip(track_inputs, sub_tab_contents)):
        label = schedule.find('label', attrs={'for': inp.get('id', '')})
        track_name = label.get_text(strip=True) if label else inp.get('id', '')
        groups = stc.find_all('div', class_='schedule__group', recursive=False)
        print(f'  [{i}] {track_name}: {len(groups)} groups')
        
        # For scientific program, look at internal structure
        if 'scientific' in track_name.lower():
            print(f'    *** Scientific Program structure ***')
            # Check for nested sub-tabs within this sub-tab-content
            nested_inputs = stc.find_all('input', type='radio')
            nested_sub_tabs = stc.find_all('div', class_='sub-tab-content')
            print(f'    Nested radio inputs: {len(nested_inputs)}')
            print(f'    Nested sub-tab-contents: {len(nested_sub_tabs)}')
            
            # Look at first few groups
            for j, grp in enumerate(groups[:3]):
                time_div = grp.find('div', class_='schedule__group-time')
                time_text = time_div.get_text(strip=True) if time_div else '?'
                items = grp.find_all('div', class_='schedule__group-item')
                print(f'    Group {j}: time={time_text}, items={len(items)}')
                for item in items:
                    desc = item.find('div', class_='schedule__group-item-description')
                    h1 = desc.find('h1') if desc else None
                    room_p = None
                    if desc:
                        for p in desc.find_all('p'):
                            strong = p.find('strong')
                            if strong and 'Room' in strong.get_text():
                                room_p = p
                                break
                    title_text = h1.get_text(strip=True)[:50] if h1 else '?'
                    room_text = room_p.get_text(strip=True)[:40] if room_p else 'no room'
                    print(f'      Item: {title_text} | {room_text}')
