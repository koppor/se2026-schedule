import xml.etree.ElementTree as ET
tree = ET.parse('schedule.xml')
root = tree.getroot()
for day in root.findall('day'):
    day_idx = day.get('index')
    for room in day.findall('room'):
        events = room.findall('event')
        starts = [e.find('start').text for e in events]
        for i in range(len(starts)-1):
            if starts[i] > starts[i+1]:
                print(f'Day {day_idx} Room={room.get("name")}: out of order: {starts[i]} then {starts[i+1]}')
print('Done checking order')

# Also show all scientific program tracks per room
print('\n--- Scientific program: parallel rooms per time ---')
sci_by_time = {}
for day in root.findall('day'):
    day_idx = day.get('index')
    for room in day.findall('room'):
        for ev in room.findall('event'):
            track = ev.find('track')
            slug = track.get('slug', '') if track is not None else ''
            if slug == 'scientific-program':
                start = ev.find('start').text
                key = (day_idx, start)
                if key not in sci_by_time:
                    sci_by_time[key] = []
                sci_by_time[key].append(room.get('name'))

for key in sorted(sci_by_time):
    rooms = sci_by_time[key]
    if len(rooms) > 1:
        print(f'Day {key[0]} {key[1]}: {rooms}')
