# Technical Specification: Session Content Expansion

## Complexity Assessment: Medium

## Technical Context

- **Language**: Python 3
- **Dependencies**: `beautifulsoup4`, `xml.etree.ElementTree`, `xml.dom.minidom`
- **Input**: `inner.html` (SE2026 schedule HTML)
- **Output**: `schedule.xml` (FOSDEM/Giggity-compatible XML)
- **Entry point**: `convert_schedule.py`

## Problem Description

Sessions (e.g., `Session: SE4AI`, `Session: Architecture & Modeling`) contain sub-items (individual talks/papers) stored in `<div class="schedule__group-item-items">`. Currently `parse_item_description` flattens sub-items into a pipe-separated `description` string on the parent event, losing the proper structure (title, speakers, duration).

The goal is to generate **individual XML events** for each sub-item so Giggity shows correct speakers and per-talk timeslots.

### Sub-item HTML Structure

```html
<div class="schedule__group-item-item">
  <h1><em><svg .../>  "Talk title here"</em></h1>
  <p><strong><svg .../> Speaker:</strong> Name (Org)</p>
  <!-- OR -->
  <p><strong><svg .../> Speakers:</strong> Name1 (Org1), Name2 (Org2)</p>
  <!-- OR -->
  <p><strong><svg .../> Author:</strong> Name (Org)</p>
  <!-- OR -->
  <p><strong><svg .../> Authors:</strong> Name1, Name2, ...</p>
  <p><strong><svg .../> Format:</strong> 17 minutes talk + 5 minutes questions</p>
</div>
```

### Format String Examples

- `"17 minutes talk + 5 minutes questions"` → 22 minutes total
- `"17 minutes talk + 7-8 minutes questions"` → 25 minutes total (use upper bound of range)
- `"17 minutes talk + 7-8 minutes Q&A"` → 25 minutes (same parsing)

## Implementation Approach

### Strategy

1. **Parse sub-items** from `schedule__group-item-items` into structured data (title, persons, duration_minutes)
2. **Calculate sequential start times**: first sub-item starts at session start; each subsequent one starts after the previous ends
3. **Generate individual events** for each sub-item, inheriting room, track, URL, day, type from the parent session
4. **Keep the parent session event** intact (without sub-item description data), so the session container remains visible in Giggity
5. **Clear sub-items from parent description** to avoid duplication

### Format Duration Parsing

Parse `"17 minutes talk + 5 minutes questions"`:
1. Extract all `(\d+)(?:-(\d+))? minutes` patterns with regex
2. Sum all extracted minute values (use upper bound for ranges)
3. Fallback: if format unparseable, divide session duration evenly among sub-items

### Event Slug and ID for Sub-items

Sub-item events use the same `make_event_slug` and `make_guid` functions, with the sub-item title as the key.

### Sub-item Event Type

Sub-item events inherit `type` from the parent (usually `"talk"`).

## Source Code Changes

### `convert_schedule.py` — only file modified

**New functions:**

1. `parse_format_minutes(format_text) -> int`  
   Parses a format string like `"17 minutes talk + 5 minutes questions"` into total minutes.  
   Returns 0 if unparseable (caller uses fallback).

2. `parse_sub_items(items_container) -> list[dict]`  
   Parses `schedule__group-item-items` div into a list of dicts:
   ```python
   {
       "title": str,
       "persons": list[str],
       "format_text": str,
       "duration_minutes": int,  # 0 = unknown
   }
   ```

**Modified functions:**

3. `parse_item_description(desc, item_div=None) -> dict`  
   Remove the sub-items block that currently appends pipe-separated lines to `description_parts`. The `description` field will no longer contain sub-item text (it becomes the parent session's own description only).

4. `extract_events(inner_soup) -> list[dict]`  
   After creating the parent session event, if sub-items exist:
   - Parse sub-items via `parse_sub_items`
   - Calculate total sub-item minutes; if total > 0 use per-item durations; otherwise divide session duration evenly
   - For each sub-item, compute `start_time` (parent start + sum of previous durations) and `duration`
   - Create individual event dicts for each sub-item with the inherited session metadata
   - Append sub-item events to `events` list (after the parent event)

## Data / XML Changes

**Before** (one event per session, description contains all talks):
```xml
<event>
  <title>Session: SE4AI</title>
  <description>"From Prompts to Templates..." | Author: Yuetian Mao | Format: ...</description>
  <persons><person>Regina Hebig (...)</person></persons>
</event>
```

**After** (parent session + individual sub-events in the same room):
```xml
<event>
  <title>Session: SE4AI</title>
  <description></description>
  <persons><person>Regina Hebig (...)</person></persons>  <!-- session chair -->
</event>
<event>
  <title>"From Prompts to Templates: ..."</title>
  <start>10:30</start>
  <duration>00:22</duration>
  <persons><person>Yuetian Mao</person></persons>
</event>
<event>
  <title>"How Toxic Can You Get? ..."</title>
  <start>10:52</start>
  <duration>00:22</duration>
  <persons><person>Simone Corbo</person>...</persons>
</event>
...
```

## Edge Cases

- **No Format field**: Use session duration / number of sub-items
- **Range in format** (`7-8 minutes`): Use upper bound
- **Non-session sub-items** (e.g., Welcome Reception items): Still expand them as individual events with parsed durations if available; otherwise divide evenly
- **Speaker field parsing**: Strip SVG icon text from strong label (use just text after label colon)
- **Duplicate dedup key**: Sub-item events use `(day_date, start_time, title, room)` as dedup key — unlikely to collide since different titles

## Verification Approach

1. Run `python convert_schedule.py` to regenerate `schedule.xml`
2. Run `python spotcheck.py` — verify sub-items now appear as separate events with correct persons
3. Manually check the "Session: Engineering Intelligent Systems" session:
   - Should have 2 child events starting at 10:30 and ~10:52
   - Each should have the correct speaker name
4. Manually check "Session: Architecture & Modeling" (4 items × 22 min = 88 min, fits in 10:30-12:00 slot)
5. Run `python validate.py` if it exists
