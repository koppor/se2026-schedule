# Bug Investigation: Remove Quotes Around Titles

## Bug Summary
The schedule.xml file contains 100 event titles that have unwanted double quotes (`"`) wrapped around them. These quotes appear in the `<title>` tags, making the titles look like: `<title>"From Prompts to Templates..."</title>` instead of `<title>From Prompts to Templates...</title>`.

## Root Cause Analysis

### Source of the Problem
The quotes originate from the **source HTML file** (`https___se2026.inf.unibe.ch_en_program_schedule_.htm`), not from the parsing script. When inspecting the inner HTML, the titles in the `<h1>` tags within `<em>` elements already contain the quotes:

```html
<h1><em>...<svg>&nbsp;"From Prompts to Templates: A Systematic Prompt Template Analysis for Real-world LLMapps"</em></h1>
```

### How the Quotes Get Into XML
The `convert_schedule.py` script extracts these titles as-is using:
- Line 119: `title = clean_text(h1_item.get_text(separator=" ", strip=True))`
- The `clean_text()` function (line 84-85) only normalizes whitespace but does not remove quotes

The script faithfully preserves whatever text is in the HTML, including the quotes that are part of the original content.

## Affected Components

### Files Affected
1. **schedule.xml** - Contains 100 titles with unwanted quotes
2. **convert_schedule.py** - The parser script that needs modification

### Pattern of Affected Titles
- All affected titles are scientific paper titles (sub-items within sessions)
- They appear in the `parse_sub_items()` function at line 112-143
- Common pattern: Titles of research papers and presentations in scientific program sessions
- Subtitles are NOT affected (0 occurrences found)

### Locations in Code
- **convert_schedule.py:119** - Where sub-item titles are extracted
- **convert_schedule.py:157** - Where main event titles are extracted (not affected)
- **convert_schedule.py:84-85** - The `clean_text()` function that could be enhanced

## Proposed Solution

### Option 1: Strip Quotes During Parsing (Recommended)
Modify the title extraction to remove leading/trailing quotes from the extracted text. This can be done by:

1. Updating the `clean_text()` function to optionally strip quotes
2. Or adding a dedicated post-processing step after line 119 and 157 to strip quotes from titles

**Advantages:**
- Handles the issue at parse time
- Clean, reusable solution
- Prevents the problem in future re-runs of the script

### Option 2: Post-Process XML
Modify the XML file directly after generation to remove quotes from title tags.

**Disadvantages:**
- Manual fix that needs to be repeated each time the script is run
- Less maintainable

## Edge Cases and Considerations

1. **Legitimate quotes in titles**: Some titles might legitimately need quotes (e.g., when quoting something). The proposed solution would remove ALL leading/trailing quotes.
   - However, examining the pattern, it appears ALL quotes are unwanted decorative quotes around the entire title

2. **Quotes in the middle of titles**: The solution should only strip leading/trailing quotes, not quotes within the title text

3. **Other quote characters**: Should check for both `"` (straight quotes) and potentially `"` `"` (curly quotes) or `'` (single quotes)

4. **Backward compatibility**: After fixing, need to verify the XML is still valid and parseable by downstream tools

## Test Strategy

1. Before fix: Count titles with quotes: 100
2. After fix: Verify 0 titles have leading/trailing quotes
3. Verify XML is well-formed
4. Spot-check several affected titles to ensure quotes are removed correctly
5. Ensure titles without quotes remain unchanged

---

## Implementation Notes

### Fix Applied
Modified the `clean_text()` function in `convert_schedule.py` (line 84-88) to strip leading and trailing quotes from all text, including:
- Straight double quotes (`"`)
- Curly double quotes (`"` and `"`)
- Single quotes (`'`)

### Code Changes
```python
def clean_text(text):
    text = re.sub(r"\s+", " ", text).strip()
    # Strip leading and trailing quotes from titles
    text = text.strip('"').strip('"').strip('"').strip("'")
    return text
```

### Test Results

**Before Fix:**
- Titles with quotes: 100
- Example: `<title>"From Prompts to Templates: A Systematic Prompt Template Analysis for Real-world LLMapps"</title>`

**After Fix:**
- Titles with quotes: 0
- Example: `<title>From Prompts to Templates: A Systematic Prompt Template Analysis for Real-world LLMapps</title>`

**Verified Examples:**
- ✅ "From Prompts to Templates..." → From Prompts to Templates...
- ✅ "How Toxic Can You Get?..." → How Toxic Can You Get?...

**XML Validation:**
- ✅ schedule.xml regenerated successfully
- ✅ Total events: 234 (157 unique + 77 duplicated breaks)
- ✅ All quotes removed from titles

### Impact
All 100 affected titles now appear without decorative quotes. The fix is permanent and will apply to future regenerations of the XML file.
