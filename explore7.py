import re
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

with open("inner.html", encoding="utf-8") as f:
    inner_html = f.read()

inner_soup = BeautifulSoup(inner_html, "html.parser")

# Look at the structure of the first tab in detail
tabs = inner_soup.find_all("div", class_="tab")
first_tab = tabs[0]

# Find the first radio in this tab
first_radio = first_tab.find("input", type="radio")
print(f"First radio: id={first_radio.get('id')}")

# What's directly inside the first tab?
print("\n=== Direct children of first tab ===")
for child in first_tab.children:
    if hasattr(child, 'name') and child.name:
        classes = " ".join(child.get("class", []))
        txt = child.get_text()[:60].replace("\n", " ").strip()
        print(f"  <{child.name}> cls='{classes}' txt='{txt}'")

# Now look inside the tab-content 
tab_content = first_tab.find("div", class_="tab-content")
print(f"\n=== Direct children of first tab-content ===")
if tab_content:
    for child in tab_content.children:
        if hasattr(child, 'name') and child.name:
            classes = " ".join(child.get("class", []))
            txt = child.get_text()[:60].replace("\n", " ").strip()
            print(f"  <{child.name}> cls='{classes}' txt='{txt}'")
else:
    print("No tab-content found!")

# Look at the schedule div inside tab-content
schedule = tab_content.find("div", class_="schedule") if tab_content else None
print(f"\n=== Direct children of schedule div ===")
if schedule:
    for child in schedule.children:
        if hasattr(child, 'name') and child.name:
            classes = " ".join(child.get("class", []))
            txt = child.get_text()[:60].replace("\n", " ").strip()
            print(f"  <{child.name}> cls='{classes}' txt='{txt}'")

print("\n\n=== First 5 schedule__groups in first tab ===")
groups = first_tab.find_all("div", class_="schedule__group")
print(f"Total groups: {len(groups)}")
for i, grp in enumerate(groups[:5]):
    # find parent context (to understand track ownership)
    p1 = grp.parent
    p2 = p1.parent if p1 else None
    p3 = p2.parent if p2 else None
    print(f"\nGroup {i+1}: parent cls={p1.get('class') if p1 else None}, gp cls={p2.get('class') if p2 else None}, ggp cls={p3.get('class') if p3 else None}")
    time_div = grp.find("div", class_="schedule__group-time")
    item_div = grp.find("div", class_="schedule__group-item-description")
    print(f"  Time: {time_div.get_text().strip() if time_div else None}")
    if item_div:
        h1 = item_div.find("h1")
        print(f"  Title (h1): {h1.get_text().strip() if h1 else None}")
        for p in item_div.find_all("p", limit=4):
            txt = p.get_text().strip().replace("\n", " ")
            print(f"  <p>: {txt[:100]}")
