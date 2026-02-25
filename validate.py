import xml.etree.ElementTree as ET
tree = ET.parse("schedule.xml")
root = tree.getroot()
print("Valid XML!")
days = root.findall("day")
print(f"Days: {len(days)}")
for day in days:
    rooms = day.findall("room")
    events_count = sum(len(r.findall("event")) for r in rooms)
    print(f"  Day {day.get('index')} ({day.get('date')}): {len(rooms)} rooms, {events_count} events")

tracks = root.findall("tracks/track")
print(f"Tracks: {len(tracks)}")
for t in tracks:
    print(f"  [{t.get('slug')}] {t.text}")
