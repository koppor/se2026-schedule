import xml.etree.ElementTree as ET
tree = ET.parse('schedule.xml')
root = tree.getroot()

print('=== Scientific Program Events (Day 3, Champions Lounge) ===')
for day in root.findall('day'):
    if day.get('index') != '3':
        continue
    for room in day.findall('room'):
        if 'Champions Lounge' not in room.get('name', '') or 'Catering' in room.get('name','') or 'Reception' in room.get('name',''):
            continue
        for ev in room.findall('event'):
            track = ev.find('track')
            slug = track.get('slug', '') if track is not None else ''
            if slug == 'scientific-program':
                print(f'  id={ev.get("id"):>4} start={ev.find("start").text} title={ev.find("title").text[:50]}')

print()
print('=== Event ID sequence for scientific-program track ===')
ids = []
for day in root.findall('day'):
    for room in day.findall('room'):
        for ev in room.findall('event'):
            track = ev.find('track')
            slug = track.get('slug', '') if track is not None else ''
            if slug == 'scientific-program':
                ids.append((int(ev.get('id')), ev.find('start').text, day.get('index'), room.get('name'), ev.find('title').text[:40]))

ids.sort()
for item in ids[:30]:
    print(f'  id={item[0]:>4} day={item[2]} start={item[1]} room={item[3][:20]} title={item[4]}')

print()
print('=== Check if IDs are sequential within each room ===')
for day in root.findall('day'):
    for room in day.findall('room'):
        evs = [(int(e.get('id')), e.find('start').text) for e in room.findall('event')]
        track = None
        for e in room.findall('event'):
            t = e.find('track')
            if t is not None and t.get('slug') == 'scientific-program':
                track = 'scientific-program'
                break
        if track and len(evs) > 1:
            id_order = [x[0] for x in evs]
            start_order = [x[1] for x in evs]
            is_id_sorted = id_order == sorted(id_order)
            is_start_sorted = start_order == sorted(start_order)
            if not is_id_sorted:
                print(f'  Day {day.get("index")} {room.get("name")}: IDs NOT in order: {id_order[:8]}')
            if not is_start_sorted:
                print(f'  Day {day.get("index")} {room.get("name")}: starts NOT in order: {start_order[:8]}')
