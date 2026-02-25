# Technical Specification: Time Ordering & Track Mapping Fix

## Difficulty: Easy-Medium

## Context

- **Language**: Python 3 with BeautifulSoup, xml.etree.ElementTree
- **Entry point**: `convert_schedule.py` → parses `inner.html` → produces `schedule.xml` (FOSDEM-style XML)
- **Viewer**: A FOSDEM-style conference app that displays events per track

## Root Cause Analysis

### Issue 1: Track mapping (primary cause of time ordering problem)

The scientific program (and similar days) has **parallel sessions** — groups at the *same* time but in *different rooms*:

```
Group 4: 10:30–12:00 → "Session: Architecture & Modeling" (Sky Lounge 1)  [4 sub-items]
Group 5: 10:30–12:00 → "Session: SE4AI"                  (Champions Lounge)[4 sub-items]
Group 6: 10:30–12:00 → "Session: Verification"            (Sky Lounge 2)   [4 sub-items]
```

All three sessions currently receive the **same track** `scientific-program`. When the conference app lists all events for the "Scientific Program" track, it shows events from three rooms mixed together:

```
Champions Lounge (CL):  09:00, 09:05, 10:30, 10:52, 11:14, 11:36, 13:30, ...
Sky Lounge 1 (SL1):             10:30, 10:52, 11:14, 11:36, 13:30, ...
Sky Lounge 2 (SL2):             10:30, 10:52, 11:14, 11:36, 13:30, ...
```

Because rooms are alphabetically sorted in the XML and each room's events are time-sorted, the flat list order is:
`09:00, 09:05, 10:30(CL), 10:52(CL), …, 10:30(SL1), 10:52(SL1), …, 10:30(SL2), …`

→ Times appear **non-monotonic** to the viewer.

### Issue 2: String sort is fine

`sorted(..., key=lambda e: e["start"])` works correctly because all times are **zero-padded** (e.g., `09:00`, `10:30`). No fix needed here.

## HTML Structure (confirmed by exploration)

- Each day tab (`div.tab`) → `div.tab-content` → `div.schedule`
- Inside `div.schedule`: radio inputs + `div.sub-tab-content` for each workshop/track
- The **scientific program** sub-tab-content has `div.schedule__group` elements
- Parallel sessions appear as **multiple groups at the same time**, each with a title like `"Session: X"` and different rooms
- Each session has 4 sub-items (individual talks)
- Plenary events (Registration, Opening, Keynote, Coffee Break, Lunch, Reception) appear as single-room groups with NO sub-items

## Proposed Fix

### In `extract_events` — per-group track override

When parsing each `schedule__group`, after `parse_item_description` yields a `title`:

1. **If** the title starts with `"Session:"` (case-insensitive):
   - Extract the session label: `title[len("Session:"):].strip()`
   - Compute a sub-track slug: `slugify(track_slug + "-" + session_label)` (stays within parent namespace)
   - Compute a sub-track name: `f"{track_name}: {session_label}"`
   - Use these **instead of** the parent `track_slug`/`track_name` for this group's events

2. **Otherwise**: keep the parent track (plenary events, breaks, keynotes, etc.)

3. Apply the overridden track to **sub-items** (individual talks within the session) and to the parent session event if it gets emitted (currently it doesn't when sub-items exist, but for correctness).

### Effect

- `"scientific-program"` track retains only plenary events (Registration, Opening, Keynotes, Breaks, Lunch, Reception)
- Each parallel session becomes its own track:
  - `"scientific-program-architecture-modeling"` → "Scientific Program (SE): Architecture & Modeling"
  - `"scientific-program-se4ai"` → "Scientific Program (SE): SE4AI"
  - `"scientific-program-verification"` → "Scientific Program (SE): Verification"
  - etc.
- Events within each track → one room → time-ordered ✓

### Days affected

| Day | Parallel sessions |
|-----|-------------------|
| Wednesday (3) | CL, Sky Lounge 1, Sky Lounge 2 at 10:30–12:00 and 13:30–15:00; CL, Sky Lounge 2 at 15:30–17:00 |
| Thursday (4) | Sky Lounge 1 & 2 at 10:30–12:00; Sky Lounge 2 & 3 at 13:30–15:00; Sky Lounge 2 at 15:30–17:00 |
| Friday (5) | CL, Sky Lounge 2, Sky Lounge 3 at 10:30–12:00 |

## Files to Modify

| File | Change |
|------|--------|
| `convert_schedule.py` | `extract_events()`: derive per-group track from session title when title matches `"Session: *"` |

## Data Model Change

No structural XML schema change. Only `<track slug="...">...</track>` values inside `<event>` elements change. The top-level `<tracks>` list will expand from 14 to ~20+ entries.

## Verification

1. Run `python convert_schedule.py` — should complete without errors
2. Check that `schedule.xml` now contains sub-tracks like `scientific-program-se4ai`
3. Verify plenary events (Opening, Keynote, Coffee Break, etc.) still have `scientific-program` track
4. Run the check scripts: `python check_order.py` — confirm no rooms have events out of time order
5. Verify event count is unchanged (sub-items are not added/removed, only re-tracked)
