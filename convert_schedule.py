#!/usr/bin/env python3
"""Convert SE2026 schedule HTML (Firefox view-source) to FOSDEM-style XML."""

import re
import sys
import uuid
from collections import defaultdict
from xml.etree.ElementTree import Element, SubElement
from xml.dom import minidom
from bs4 import BeautifulSoup

INPUT_FILE = "https___se2026.inf.unibe.ch_en_program_schedule_.htm"
OUTPUT_FILE = "schedule.xml"
BASE_URL = "https://se2026.inf.unibe.ch/en/program/schedule/"
SCHEDULE_NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")

DAY_INFO = {
    "monday":    {"date": "2026-02-23", "index": 1, "label": "Monday, 23 February"},
    "tuesday":   {"date": "2026-02-24", "index": 2, "label": "Tuesday, 24 February"},
    "wednesday": {"date": "2026-02-25", "index": 3, "label": "Wednesday, 25 February"},
    "thursday":  {"date": "2026-02-26", "index": 4, "label": "Thursday, 26 February"},
    "friday":    {"date": "2026-02-27", "index": 5, "label": "Friday, 27 February"},
}


def extract_inner_html(filepath):
    with open(filepath, encoding="utf-8") as f:
        outer_html = f.read()
    outer_soup = BeautifulSoup(outer_html, "html.parser")
    line_spans = outer_soup.find_all("span", id=re.compile(r"^line\d+$"))
    return "\n".join(span.get_text() for span in line_spans)


def slugify(text):
    s = text.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    s = re.sub(r"-+", "-", s)
    return s[:60].strip("-")


def make_event_slug(acronym, event_id, title):
    return f"{acronym}-{event_id}-{slugify(title)}"


def make_guid(slug):
    return str(uuid.uuid5(SCHEDULE_NS, slug))


def parse_time_minutes(t):
    h, m = t.strip().split(":")
    return int(h) * 60 + int(m)


def add_minutes_to_time(time_str, minutes):
    total = parse_time_minutes(time_str) + minutes
    return f"{total // 60:02d}:{total % 60:02d}"


def minutes_to_duration(minutes):
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def compute_duration(start_str, end_str):
    start = parse_time_minutes(start_str)
    end = parse_time_minutes(end_str)
    dur = (end - start) % (24 * 60)
    return f"{dur // 60:02d}:{dur % 60:02d}"


def get_strong_label(element):
    strong = element.find("strong", recursive=False)
    if strong:
        return strong.get_text(strip=True)
    return ""


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


ROOM_ALIASES = {
    re.compile(r"^Champions Lounge\b.*"): "Champions Lounge",
}


def normalize_room(name):
    for pattern, canonical in ROOM_ALIASES.items():
        if pattern.match(name):
            return canonical
    return name


def parse_format_minutes(format_text):
    """Parse a format string like '17 minutes talk + 5 minutes questions' into total minutes."""
    total = 0
    found = False
    for m in re.finditer(r"(\d+)(?:-(\d+))?\s+minutes?", format_text, re.IGNORECASE):
        found = True
        low = int(m.group(1))
        high = int(m.group(2)) if m.group(2) else low
        total += high
    return total if found else 0


def parse_sub_items(items_container):
    """Parse schedule__group-item-items div into a list of dicts."""
    sub_items = []
    for item in items_container.find_all("div", class_="schedule__group-item-item"):
        h1_item = item.find("h1")
        if not h1_item:
            continue
        title = clean_text(h1_item.get_text(separator=" ", strip=True))
        persons = []
        format_text = ""
        duration_minutes = 0
        for p in item.find_all("p"):
            label = get_strong_label(p)
            full_text = clean_text(p.get_text(separator=" ", strip=True))
            if label:
                value = full_text[len(label):].strip()
                label_lower = label.lower().rstrip(":")
                if label_lower in ("speaker", "speakers", "author", "authors"):
                    for name in re.split(r",\s*(?=[A-Z])", value):
                        name = name.strip()
                        if name:
                            persons.append(name)
                elif label_lower == "format":
                    format_text = value
                    duration_minutes = parse_format_minutes(value)
        sub_items.append({
            "title": title,
            "persons": persons,
            "format_text": format_text,
            "duration_minutes": duration_minutes,
        })
    return sub_items


def parse_item_description(desc, item_div=None):
    result = {
        "title": "",
        "room": "",
        "link_href": "",
        "persons": [],
        "description": "",
    }

    h1 = desc.find("h1")
    if h1:
        result["title"] = clean_text(h1.get_text(separator=" ", strip=True))

    description_parts = []

    for child in desc.children:
        if not hasattr(child, "name") or not child.name:
            continue

        if child.name == "p":
            label = get_strong_label(child)
            full_text = clean_text(child.get_text(separator=" ", strip=True))

            if label:
                value = full_text[len(label):].strip()

                if label == "Room:":
                    result["room"] = normalize_room(value)
                elif label == "Location:":
                    if not result["room"]:
                        result["room"] = normalize_room(value)
                elif label == "Link:":
                    a = child.find("a")
                    if a:
                        result["link_href"] = a.get("href", "")
                elif label in ("Speaker:", "Session Chair:"):
                    if value:
                        result["persons"].append(value)
            else:
                if full_text:
                    description_parts.append(full_text)

        elif child.name == "div" and "schedule__list" in child.get("class", []):
            for li in child.find_all("li"):
                figcaption = li.find("figcaption")
                if figcaption:
                    name = clean_text(figcaption.get_text(separator=" ", strip=True))
                else:
                    name = clean_text(li.get_text(separator=" ", strip=True))
                if name:
                    result["persons"].append(name)

    result["description"] = "\n".join(description_parts)
    return result


def get_event_type(title):
    t = title.lower()
    if "keynote" in t:
        return "keynote"
    if "opening" in t or "closing" in t:
        return "other"
    if "registration" in t:
        return "other"
    if "coffee" in t or "break" in t:
        return "other"
    if "lunch" in t:
        return "other"
    if "reception" in t or "dinner" in t:
        return "other"
    if "session:" in t:
        return "talk"
    if any(x in t for x in ["talks", "presentations", "panel", "discussion"]):
        return "talk"
    return "other"


def get_language(title):
    if "keynote" in title.lower():
        return "en"
    return "de"


def extract_events(inner_soup):
    events = []
    event_id = 1
    seen = set()

    tabs = inner_soup.find_all("div", class_="tab")

    for tab in tabs:
        radio = tab.find("input", type="radio")
        if not radio:
            continue
        radio_id = radio.get("id", "")
        day_key = None
        for day in DAY_INFO:
            if day in radio_id:
                day_key = day
                break
        if day_key is None:
            continue

        day_date = DAY_INFO[day_key]["date"]

        tab_content = tab.find("div", class_="tab-content")
        if not tab_content:
            continue

        schedule = tab_content.find("div", class_="schedule")
        if not schedule:
            continue

        track_inputs = schedule.find_all("input", type="radio")
        sub_tab_contents = schedule.find_all("div", class_="sub-tab-content", recursive=False)

        for idx, sub_content in enumerate(sub_tab_contents):
            if idx < len(track_inputs):
                track_radio_id = track_inputs[idx].get("id", "")
                track_slug = re.sub(
                    r"^radio-(monday|tuesday|wednesday|thursday|friday)-", "",
                    track_radio_id,
                )
                label_el = schedule.find("label", attrs={"for": track_radio_id})
                track_name = clean_text(
                    label_el.get_text(separator=" ", strip=True) if label_el else track_slug
                )
                track_name = re.sub(r"\s*[\u25be\u25b8\u25b6\u25bc\u25b6]+\s*$", "", track_name).strip()
            else:
                track_slug = "unknown"
                track_name = "Unknown"

            groups = sub_content.find_all("div", class_="schedule__group", recursive=False)

            for grp in groups:
                time_div = grp.find("div", class_="schedule__group-time")
                if not time_div:
                    continue
                spans = time_div.find_all("span")
                if len(spans) < 2:
                    continue
                start_time = spans[0].get_text(strip=True)
                end_time = spans[1].get_text(strip=True)

                item_div = grp.find("div", class_="schedule__group-item")
                if not item_div:
                    continue
                desc = item_div.find("div", class_="schedule__group-item-description")
                if not desc:
                    continue

                parsed = parse_item_description(desc, item_div)
                title = parsed["title"]
                room = parsed["room"]

                dedup_key = (day_date, start_time, title, room)
                if dedup_key in seen:
                    continue
                seen.add(dedup_key)

                effective_track_slug = track_slug
                effective_track_name = track_name
                if title.lower().startswith("session:"):
                    session_label = title[len("session:"):].strip()
                    effective_track_slug = slugify(track_slug + "-" + session_label)
                    effective_track_name = f"{track_name}: {session_label}"

                duration = compute_duration(start_time, end_time)
                slug = make_event_slug("se2026", event_id, title)
                guid = make_guid(slug)
                event_type = get_event_type(title)
                language = get_language(title)

                link_href = parsed["link_href"]
                if link_href and not link_href.startswith("http"):
                    link_href = "https://se2026.inf.unibe.ch" + link_href
                event_url = link_href if link_href else BASE_URL

                event = {
                    "id": event_id,
                    "guid": guid,
                    "slug": slug,
                    "url": event_url,
                    "day_date": day_date,
                    "day_index": DAY_INFO[day_key]["index"],
                    "start": start_time,
                    "duration": duration,
                    "title": title,
                    "room": room,
                    "track_slug": effective_track_slug,
                    "track_name": effective_track_name,
                    "type": event_type,
                    "language": language,
                    "persons": parsed["persons"],
                    "abstract": "",
                    "description": parsed["description"],
                }
                items_container = item_div.find("div", class_="schedule__group-item-items")
                sub_items = []
                if items_container:
                    sub_items = parse_sub_items(items_container)

                if sub_items:
                    session_total_minutes = parse_time_minutes(end_time) - parse_time_minutes(start_time)
                    total_known = sum(si["duration_minutes"] for si in sub_items)
                    if total_known == 0:
                        even_minutes = session_total_minutes // len(sub_items)
                        for si in sub_items:
                            si["duration_minutes"] = even_minutes

                    sub_start = start_time
                    for si in sub_items:
                        sub_dur_min = si["duration_minutes"]
                        sub_duration = minutes_to_duration(sub_dur_min)
                        sub_slug = make_event_slug("se2026", event_id, si["title"])
                        sub_guid = make_guid(sub_slug)
                        sub_dedup = (day_date, sub_start, si["title"], room)
                        if sub_dedup not in seen:
                            seen.add(sub_dedup)
                            sub_event = {
                                "id": event_id,
                                "guid": sub_guid,
                                "slug": sub_slug,
                                "url": event_url,
                                "day_date": day_date,
                                "day_index": DAY_INFO[day_key]["index"],
                                "start": sub_start,
                                "duration": sub_duration,
                                "title": si["title"],
                                "room": room,
                                "track_slug": effective_track_slug,
                                "track_name": effective_track_name,
                                "type": event_type,
                                "language": language,
                                "persons": si["persons"],
                                "abstract": "",
                                "description": si["format_text"],
                            }
                            events.append(sub_event)
                            event_id += 1
                        sub_start = add_minutes_to_time(sub_start, sub_dur_min)
                else:
                    events.append(event)
                    event_id += 1

    return events


def collect_tracks(events):
    seen = {}
    for ev in events:
        slug = ev["track_slug"]
        if slug not in seen:
            seen[slug] = ev["track_name"]
    return seen


def build_xml(events):
    tracks = collect_tracks(events)

    root = Element("schedule")
    ver = SubElement(root, "version")
    ver.text = "latest"

    conf = SubElement(root, "conference")
    SubElement(conf, "acronym").text = "se2026"
    SubElement(conf, "title").text = "SE 2026"
    SubElement(conf, "subtitle").text = ""
    SubElement(conf, "venue").text = "Wankdorf Stadium / Workspace Welle7"
    SubElement(conf, "city").text = "Bern"
    SubElement(conf, "start").text = "2026-02-23"
    SubElement(conf, "end").text = "2026-02-27"
    SubElement(conf, "days").text = "5"
    SubElement(conf, "day_change").text = "09:00:00"
    SubElement(conf, "timeslot_duration").text = "00:05:00"
    SubElement(conf, "base_url").text = BASE_URL
    SubElement(conf, "time_zone_name").text = "Europe/Zurich"

    tracks_el = SubElement(root, "tracks")
    for slug, name in tracks.items():
        t = SubElement(tracks_el, "track")
        t.set("slug", slug)
        t.text = name

    by_day = defaultdict(list)
    for ev in events:
        by_day[ev["day_index"]].append(ev)

    for day_index in sorted(by_day.keys()):
        day_events = by_day[day_index]
        day_date = day_events[0]["day_date"]
        start_dt = f"{day_date}T09:00:00+01:00"
        next_date = f"2026-02-{23 + day_index - 1 + 1:02d}"
        end_dt = f"{next_date}T08:59:00+01:00"

        day_el = SubElement(root, "day")
        day_el.set("index", str(day_index))
        day_el.set("date", day_date)
        day_el.set("start", start_dt)
        day_el.set("end", end_dt)

        by_room = defaultdict(list)
        for ev in day_events:
            by_room[ev["room"]].append(ev)

        for room_name in sorted(by_room.keys()):
            room_events = sorted(by_room[room_name], key=lambda e: e["start"])
            room_slug = slugify(room_name)

            room_el = SubElement(day_el, "room")
            room_el.set("name", room_name)
            room_el.set("slug", room_slug)

            for ev in room_events:
                event_date = f"{ev['day_date']}T{ev['start']}:00+01:00"

                event_el = SubElement(room_el, "event")
                event_el.set("guid", ev["guid"])
                event_el.set("id", str(ev["id"]))

                SubElement(event_el, "date").text = event_date
                SubElement(event_el, "start").text = ev["start"]
                SubElement(event_el, "duration").text = ev["duration"]
                SubElement(event_el, "room").text = ev["room"]
                SubElement(event_el, "slug").text = ev["slug"]
                SubElement(event_el, "url").text = ev["url"]
                SubElement(event_el, "title").text = ev["title"]
                SubElement(event_el, "subtitle").text = ""

                track_el = SubElement(event_el, "track")
                track_el.set("slug", ev["track_slug"])
                track_el.text = ev["track_name"]

                SubElement(event_el, "type").text = ev["type"]
                SubElement(event_el, "language").text = ev["language"]
                SubElement(event_el, "abstract").text = ""
                SubElement(event_el, "description").text = ev["description"]

                persons_el = SubElement(event_el, "persons")
                for pid, name in enumerate(ev["persons"], start=1):
                    p_el = SubElement(persons_el, "person")
                    p_el.set("id", str(pid))
                    p_el.text = name

                SubElement(event_el, "attachments")
                SubElement(event_el, "links")

    return root


def indent_xml(root):
    xml_str = minidom.parseString(
        b'<?xml version="1.0" encoding="UTF-8"?>' + _tostring(root)
    ).toprettyxml(indent="  ", encoding="UTF-8")
    return xml_str


def _tostring(element):
    from xml.etree.ElementTree import tostring
    return tostring(element, encoding="unicode").encode("utf-8")


def main():
    print(f"Reading {INPUT_FILE} ...", file=sys.stderr)
    inner_html = extract_inner_html(INPUT_FILE)

    print("Parsing inner HTML ...", file=sys.stderr)
    inner_soup = BeautifulSoup(inner_html, "html.parser")

    print("Extracting events ...", file=sys.stderr)
    events = extract_events(inner_soup)
    print(f"  Found {len(events)} unique events", file=sys.stderr)

    print("Building XML ...", file=sys.stderr)
    root = build_xml(events)

    print(f"Writing {OUTPUT_FILE} ...", file=sys.stderr)
    xml_bytes = indent_xml(root)
    with open(OUTPUT_FILE, "wb") as f:
        f.write(xml_bytes)

    print("Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
