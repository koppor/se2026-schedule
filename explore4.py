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

# Find all schedule divs (day containers)
schedule_divs = inner_soup.find_all("div", class_="schedule")
print(f"Found {len(schedule_divs)} schedule containers (tabs/tracks)")

# Look at the structure of day containers
# The structure is: div.accordion > input[checkbox] + label + div.accordion-content > div.tabs > input[radio] + ...
# Let's look at what wraps the schedule divs

print("\n=== Schedule div parents ===")
for i, sch in enumerate(schedule_divs[:3]):
    parent = sch.parent
    grandparent = parent.parent if parent else None
    print(f"\n--- Schedule {i+1} ---")
    print(f"Parent tag: {parent.name}, classes: {parent.get('class')}")
    if grandparent:
        print(f"GrandParent tag: {grandparent.name}, classes: {grandparent.get('class')}")

# Look at a full schedule group item
print("\n\n=== First schedule__group-item (full HTML) ===")
first_item = inner_soup.find("div", class_="schedule__group-item")
print(str(first_item)[:3000])

print("\n\n=== schedule__group-item-description ===")
desc = inner_soup.find("div", class_="schedule__group-item-description")
print(str(desc)[:2000])

# Check tabs structure
print("\n\n=== Looking for day/tab labels ===")
labels = inner_soup.find_all("label", for_=re.compile(r"(checkbox|radio)"))
for lbl in labels[:25]:
    txt = lbl.get_text().strip().replace("\n", " ")
    txt = re.sub(r'\s+', ' ', txt)
    print(f"  for={lbl.get('for')}: {txt[:80]}")
