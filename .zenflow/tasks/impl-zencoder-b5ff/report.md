# Implementation Report

## What was implemented

Created `convert_schedule.py` — a Python script that converts the SE2026 schedule HTML file (Firefox view-source format) to a FOSDEM-style XML schedule.

**Output**: `schedule.xml` with:
- 5 days (Monday–Friday, Feb 23–27, 2026)
- 93 unique events across 31 rooms
- 14 tracks (ASE, EAPROG, Q-STAV, RDMxSE, AvioSE, GenSE, SECPPS, Scientific Program, CHOOSE Forum, GI/SWT/AI4SA, Industry Day, Student Research Competition, Dissertationspreis, SEUH)
- Full conference metadata, GUID per event (UUID5), slugs, persons, descriptions with paper sub-items

**Key implementation steps**:
1. Parse the Firefox view-source HTML: extract `<span id="lineN">` text content to reconstruct the original SE2026 HTML
2. Parse the inner HTML structure: `div.tab` (one per day) → `div.schedule` → `div.sub-tab-content` (one per track) → `div.schedule__group` (time slot)
3. Extract event fields from `schedule__group-item-description`: title (h1), room (p with "Room:"), link (p with "Link:" anchor), persons (inline p or `div.schedule__list` with figcaption/li elements), description (plain p elements), sub-items from sibling `schedule__group-item-items` div
4. Deduplicate events by (day_date, start_time, title, room) to avoid shared events (registration, coffee break, lunch) appearing once per track
5. Generate FOSDEM XML grouped by (day → room → event)

## How the solution was tested

1. Ran the script: `python convert_schedule.py` — succeeded, 93 events extracted
2. Validated XML well-formedness with `xml.etree.ElementTree.parse()`
3. Manual spot-checks:
   - Verified "Opening" on Wednesday (09:00, Timo Kehrer) and Thursday (09:05 Industry Keynote with Amandine Le Pape)
   - Verified paper sessions include sub-item titles and authors in description
   - Verified keynote type assignment for "Scientific Keynote: Maria Christakis" and "Scientific Keynote: Chunyang Chen"
   - Verified persons extracted from both inline `<p>Speaker:</p>` and `<div class="schedule__list picture">` with figcaptions
   - Verified organisation persons from `<div class="schedule__list">` with `<ul><li>` items
4. All 5 days present, event counts reasonable (11–27 per day)

## Biggest challenges

1. **Firefox view-source format**: The HTM file is a Firefox view-source rendered page where the original HTML is encoded as syntax-highlighted spans. Had to first extract text from each `<span id="lineN">` to reconstruct the original HTML.

2. **HTML structure navigation**: The schedule uses a nested tab-within-tab structure (`div.tab` per day → `div.schedule` → `div.sub-tab-content` per track). The mapping between radio inputs/labels and sub-tab-content divs required careful index-based pairing.

3. **Sub-items sibling issue**: The `div.schedule__group-item-items` (containing paper presentations) is a sibling of `div.schedule__group-item-description`, not a child — required passing `item_div` to the parser rather than just `desc`.

4. **Persons extraction complexity**: Speakers/organisers appear in three different HTML patterns: (a) inline `<p><strong>Speaker:</strong> name</p>`, (b) `<div class="schedule__list picture">` with `<figure>/<figcaption>` structure, (c) `<div class="schedule__list">` with plain `<ul><li>` items.
