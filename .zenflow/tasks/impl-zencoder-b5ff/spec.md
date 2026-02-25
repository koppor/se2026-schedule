# Technical Specification: SE2026 Schedule HTML → FOSDEM XML Converter

## Complexity Assessment: Medium

The task involves parsing a non-standard input format (Firefox view-source HTML), extracting structured schedule data from a complex HTML page, and generating a FOSDEM-style XML output.

---

## Technical Context

- **Language**: Python 3
- **Dependencies**: `beautifulsoup4`, `lxml` (HTML/XML parsing) — standard library `xml.etree.ElementTree` or `lxml` for XML output; `uuid` for GUID generation; `re` for text processing
- **Input file**: `C:\Users\olive\ZenflowProjects\se-2026-schedule\https___se2026.inf.unibe.ch_en_program_schedule_.htm`
  - This is a **Firefox view-source rendered HTML file** — the original HTML source of the SE2026 schedule page is embedded as syntax-highlighted text within `<span id="lineN">` elements
- **Example XML**: `C:\Users\olive\ZenflowProjects\se-2026-schedule\xml` (FOSDEM 2025 schedule format)
- **Output**: `C:\Users\olive\ZenflowProjects\se-2026-schedule\schedule.xml`

---

## Input File Analysis

### Firefox View-Source Format
The `.htm` file is a Firefox "view-source:" saved page. Its structure:
```html
<body id="viewsource">
  <span id="line1">... (encoded HTML source line 1) ...</span>
  <span id="line2">... (encoded HTML source line 2) ...</span>
  ...
</body>
```
Each `<span id="lineN">` element contains ONE line of the original SE2026 HTML, with HTML tags encoded as spans with CSS classes (`start-tag`, `end-tag`, `attribute-name`, `attribute-value`, etc.) and text content as plain text nodes.

**Extraction strategy**: For each `<span id="lineN">`, collect the text content — this yields the original source text line (HTML entities like `&lt;` appear as `<` in text, since Firefox renders them in the span text).

Actually, the original HTML source is embedded as text — the inner spans just highlight the syntax. Getting `.get_text()` on each line span gives the original HTML source text for that line.

### SE2026 Schedule HTML Structure
The extracted HTML has:
- **Day accordion/tabs**: `<input type="checkbox" id="checkbox-monday">`, `<input type="checkbox" id="checkbox-tuesday">`, etc.
- **Track tabs within each day**: `<input type="radio" name="radiobutton-radio-monday" id="radio-monday-ase">` etc.
- **Schedule entries**: grouped by day and track, structured with time slots

From the live website content, a schedule entry pattern is:
```
TIME_SLOT (e.g., "13:00 – 13:30")
EVENT_TITLE
Room: ROOM_NAME
Link: TRACK_LINK
Speaker/Authors: ...
Description/Abstract: ...
```

The HTML likely uses divs or articles for time-slot entries with data attributes or class names encoding time/event data.

---

## Implementation Approach

### Step 1: Extract Inner HTML from Firefox View-Source File
Parse the outer Firefox HTML with BeautifulSoup. For each `<span id="lineN">`, call `.get_text()` to get the original source text. Join with newlines to reconstruct the SE2026 HTML source.

### Step 2: Parse SE2026 HTML
Parse the reconstructed HTML and extract:
- Conference metadata (name, dates, venue)
- Days (Monday–Friday, Feb 23–27, 2026)
- For each day: tracks
- For each time slot: event title, time range (start/end → duration), room, speakers/authors, abstract, track, type (session/keynote/registration/etc.)

### Step 3: Generate FOSDEM XML
Produce the XML format matching the example:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<schedule>
  <version>latest</version>
  <conference>
    <acronym>se2026</acronym>
    <title>SE 2026</title>
    <subtitle></subtitle>
    <venue>Wankdorf Stadium / Workspace Welle7</venue>
    <city>Bern</city>
    <start>2026-02-23</start>
    <end>2026-02-27</end>
    <days>5</days>
    <day_change>09:00:00</day_change>
    <timeslot_duration>00:05:00</timeslot_duration>
    <base_url>https://se2026.inf.unibe.ch/en/program/schedule/</base_url>
    <time_zone_name>Europe/Zurich</time_zone_name>
  </conference>
  <tracks>
    <track slug="scientific-program">Scientific Program (SE)</track>
    <track slug="industry-day">Industry Day</track>
    ...
  </tracks>
  <day index="1" date="2026-02-23" start="2026-02-23T09:00:00+01:00" end="2026-02-24T08:59:00+01:00">
    <room name="Reception (3rd Floor)" slug="reception-3rd-floor">
      <event guid="..." id="1">
        <date>2026-02-23T13:00:00+01:00</date>
        <start>13:00</start>
        <duration>00:30</duration>
        <room>Reception (3rd Floor)</room>
        <slug>se2026-1-registration</slug>
        <url>https://se2026.inf.unibe.ch/en/program/schedule/</url>
        <title>Registration</title>
        <subtitle></subtitle>
        <track slug="...">...</track>
        <type>other</type>
        <language>de</language>
        <abstract></abstract>
        <description></description>
        <persons></persons>
        <attachments></attachments>
        <links></links>
      </event>
    </room>
  </day>
</schedule>
```

### Key Mapping Decisions
- **Duration**: parsed from "HH:MM – HH:MM" time ranges → compute difference
- **GUID**: generated as deterministic UUID5 from event slug (namespace UUID + slug)
- **ID**: sequential integer
- **Slug**: normalized from title (lowercase, hyphens)
- **Track**: from the sub-track/session context
- **Type**: inferred from title keywords (keynote, session, registration, coffee break, lunch, etc.)
- **Language**: default "de" (German-speaking SE conference), "en" for keynotes
- **Room**: extracted from "Room: ..." text in entry
- **Persons**: parsed from "Speaker:", "Authors:", "Organisation:" fields

---

## Source File Structure

```
C:\Users\olive\ZenflowProjects\se-2026-schedule\
├── convert_schedule.py          ← NEW: main conversion script
├── https___se2026..._.htm       ← input (existing)
├── xml                          ← FOSDEM XML example (existing)
└── schedule.xml                 ← output (generated)
```

---

## Verification Approach

1. Run `python convert_schedule.py` — should produce `schedule.xml` without errors
2. Validate XML is well-formed: `python -c "import xml.etree.ElementTree as ET; ET.parse('schedule.xml'); print('Valid XML')"`
3. Manual spot-check: verify a few events match the website schedule (e.g., "Registration" on Monday at 13:00, "Opening" on Wednesday at 09:00)
4. Check event count is reasonable (~50–100 events across 5 days)
5. Verify all days (Mon–Fri) are present in output

---

## Edge Cases & Challenges

1. **Firefox view-source parsing**: The inner HTML is reconstructed from text nodes of the span elements. Some HTML entities may be double-encoded — need careful handling.
2. **Multiple tracks per day**: Monday/Tuesday have parallel tracks (e.g., ASE, EAPROG, Q-STAV, RDMxSE on Monday) — same time slot appears in different tracks. These should be separate events in different rooms.
3. **Recurring descriptions**: Workshop descriptions repeat across multiple time slots — deduplicate or keep as-is.
4. **Sessions with sub-talks**: Wednesday–Friday sessions contain multiple paper presentations within one time slot. Each sub-talk should be a separate event, or the session itself as one event (simpler approach: one event per time slot).
5. **Missing data**: Some fields like `guid`, `url`, `slug` must be generated synthetically.
6. **Time zones**: CET (UTC+1) for February dates in Bern, Switzerland.
