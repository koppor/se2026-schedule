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

# Save inner HTML for manual inspection
with open("inner.html", "w", encoding="utf-8") as f:
    f.write(inner_html)
print("Saved inner HTML to inner.html")

# Structure analysis
# Look for the tabs structure
print("\n=== Tab divs and their parents ===")
tabs = inner_soup.find_all("div", class_="tab")
for i, tab in enumerate(tabs):
    radio = tab.find("input", type="radio")
    # Traverse up to find day context (parent of parent chains)
    p1 = tab.parent
    p2 = p1.parent if p1 else None
    p3 = p2.parent if p2 else None
    print(f"\nTab {i+1}: radio={radio.get('id') if radio else None}")
    print(f"  p1: {p1.name} cls={p1.get('class') if p1 else None}")
    print(f"  p2: {p2.name} cls={p2.get('class') if p2 else None}")
    print(f"  p3: {p3.name} cls={p3.get('class') if p3 else None}")
    
    # Count schedule groups
    groups = tab.find_all("div", class_="schedule__group")
    print(f"  schedule groups in tab: {len(groups)}")

print("\n=== All schedule divs and their parents ===")
for i, sch in enumerate(inner_soup.find_all("div", class_="schedule")):
    p1 = sch.parent
    p2 = p1.parent if p1 else None
    p3 = p2.parent if p2 else None
    p4 = p3.parent if p3 else None
    groups = sch.find_all("div", class_="schedule__group", recursive=False)
    print(f"\nSchedule {i+1}:")
    print(f"  p1: {p1.name if p1 else None} cls={p1.get('class') if p1 else None}")
    print(f"  p2: {p2.name if p2 else None} cls={p2.get('class') if p2 else None}")
    print(f"  p3: {p3.name if p3 else None} cls={p3.get('class') if p3 else None}")
    print(f"  p4: {p4.name if p4 else None} cls={p4.get('class') if p4 else None}")
    print(f"  direct schedule__group children: {len(groups)}")
