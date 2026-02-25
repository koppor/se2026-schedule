import sys
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

tree = ET.parse("schedule.xml")
root = tree.getroot()

print("=== Sample events from each day ===\n")
for day in root.findall("day"):
    print(f"-- Day {day.get('index')} ({day.get('date')}) --")
    events_shown = 0
    for room in day.findall("room"):
        for event in room.findall("event"):
            if events_shown >= 3:
                break
            title = event.findtext("title")
            start = event.findtext("start")
            dur = event.findtext("duration")
            room_name = event.findtext("room")
            track = event.find("track")
            track_name = track.text if track is not None else ""
            etype = event.findtext("type")
            persons = [p.text for p in event.findall("persons/person")]
            desc = event.findtext("description") or ""
            print(f"  [{start} +{dur}] {title} | Room: {room_name} | Track: {track_name} | Type: {etype}")
            if persons:
                print(f"    Persons: {', '.join(persons[:3])}")
            if desc:
                print(f"    Desc: {desc[:100]}...")
            events_shown += 1
        if events_shown >= 3:
            break
    print()

print("=== Events with sub-items (sessions with papers) ===\n")
count = 0
for day in root.findall("day"):
    for room in day.findall("room"):
        for event in room.findall("event"):
            desc = event.findtext("description") or ""
            if " | " in desc:
                title = event.findtext("title")
                start = event.findtext("start")
                day_date = day.get("date")
                print(f"  [{day_date} {start}] {title}")
                for line in desc.split("\n")[:3]:
                    print(f"    {line[:120]}")
                count += 1
                if count >= 5:
                    break
        if count >= 5:
            break
    if count >= 5:
        break

print(f"\nTotal events: {sum(len(r.findall('event')) for d in root.findall('day') for r in d.findall('room'))}")
