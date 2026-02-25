import re
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

with open("https___se2026.inf.unibe.ch_en_program_schedule_.htm", encoding="utf-8") as f:
    outer_html = f.read()

outer_soup = BeautifulSoup(outer_html, "html.parser")
lines = outer_soup.find_all("span", id=re.compile(r"^line\d+$"))
inner_lines = [span.get_text() for span in lines]
inner_html = "\n".join(inner_lines)

inner_soup = BeautifulSoup(inner_html, "html.parser")

# The structure:
# div.accordion > input[checkbox-monday] + label + div.accordion-content > div.tabs > [input[radio] + div.tab]...
# Each div.tab has a div.tab-content > div.schedule > div.schedule__group*

# Let's traverse the accordion structure
accordions = inner_soup.find_all("div", class_="accordion")
print(f"Found {len(accordions)} accordions (days)")

# Find the actual day containers
# The checkbox inputs are: checkbox-monday, checkbox-tuesday, etc.
DAY_IDS = ["checkbox-monday", "checkbox-tuesday", "checkbox-wednesday", "checkbox-thursday", "checkbox-friday"]
DAY_DATES = {
    "monday": "2026-02-23",
    "tuesday": "2026-02-24",
    "wednesday": "2026-02-25",
    "thursday": "2026-02-26",
    "friday": "2026-02-27",
}

# Find all tab divs - each tab corresponds to a track within a day
tabs = inner_soup.find_all("div", class_="tab")
print(f"Found {len(tabs)} tabs (track-per-day tabs)")

# Each tab has: input[radio] + label + div.tab-content
for i, tab in enumerate(tabs[:3]):
    radio = tab.find("input", type="radio")
    label = tab.find("label")
    tab_content = tab.find("div", class_="tab-content")
    schedule = tab_content.find("div", class_="schedule") if tab_content else None
    print(f"\nTab {i+1}: radio_id={radio.get('id') if radio else None}, label={label.get_text()[:50] if label else None}")
    if schedule:
        groups = schedule.find_all("div", class_="schedule__group", recursive=False)
        print(f"  Schedule groups: {len(groups)}")

print("\n\n=== Examining parent structure of tabs ===")
# Look at the full structure around tabs
first_accordion_html = str(inner_soup.find_all("div", class_="accordion")[0])[:200]
print(f"First accordion start: {first_accordion_html}")

# Get structure: div.accordion-content > div.tabs > div.tab
acc_contents = inner_soup.find_all("div", class_="accordion-content")
print(f"\nFound {len(acc_contents)} accordion-content divs (day content areas)")
for i, acc in enumerate(acc_contents):
    tabs_in_acc = acc.find_all("div", class_="tab")
    print(f"  Accordion {i+1}: {len(tabs_in_acc)} tabs")
    for tab in tabs_in_acc:
        radio = tab.find("input", type="radio")
        if radio:
            print(f"    Track id: {radio.get('id')}")

print("\n\n=== Full example of a schedule group ===")
# Get a more interesting group with multiple items
for grp in inner_soup.find_all("div", class_="schedule__group"):
    items_div = grp.find("div", class_="schedule__group-item-items")
    if items_div:
        print(str(grp)[:3000])
        break
