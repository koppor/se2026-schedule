from xml.etree import ElementTree as ET
tree = ET.parse('schedule.xml')
root = tree.getroot()
for day in root.findall('day'):
    for room in day.findall('room'):
        for ev in room.findall('event'):
            track = ev.find('track')
            slug = track.get('slug', '') if track is not None else ''
            ttext = track.text or '' if track is not None else ''
            if 'scientific' in slug.lower() or 'scientific' in ttext.lower():
                print(f'Day {day.get("index")} Room={room.get("name")} Start={ev.find("start").text} Title={ev.find("title").text[:60]}')
