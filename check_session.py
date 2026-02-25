import xml.etree.ElementTree as ET
import sys
sys.stdout.reconfigure(encoding='utf-8')
tree = ET.parse('schedule.xml')
root = tree.getroot()

print("=== All events in Sky Lounge 3 ===")
for day in root.findall('day'):
    for room in day.findall('room'):
        if 'Sky Lounge' in (room.get('name') or ''):
            for event in room.findall('event'):
                title = event.findtext('title') or ''
                start = event.findtext('start')
                dur = event.findtext('duration')
                persons = [p.text for p in event.findall('persons/person')]
                print(f'[{start} +{dur}] {title}')
                if persons:
                    print(f'  Persons: {persons[:2]}')

print()
print("=== SE4AI sub-events ===")
for day in root.findall('day'):
    for room in day.findall('room'):
        for event in room.findall('event'):
            title = event.findtext('title') or ''
            start = event.findtext('start')
            if start == '10:30' and 'Session' not in title:
                dur = event.findtext('duration')
                persons = [p.text for p in event.findall('persons/person')]
                print(f'[{start} +{dur}] {title[:80]}')
                if persons:
                    print(f'  Persons: {persons[:2]}')

print()
print('Total events:', sum(len(r.findall('event')) for d in root.findall('day') for r in d.findall('room')))
