import re
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

with open("inner.html", encoding="utf-8") as f:
    inner_html = f.read()

inner_soup = BeautifulSoup(inner_html, "html.parser")

# Look at a group with speakers
for grp in inner_soup.find_all("div", class_="schedule__group"):
    desc = grp.find("div", class_="schedule__group-item-description")
    if desc:
        for p in desc.find_all("p"):
            txt = p.get_text().strip()
            if "Speaker" in txt or "Author" in txt:
                print("=== Full group with speakers ===")
                print(str(grp)[:3000])
                break

# Look at the schedule list (schedule__list)
print("\n\n=== schedule__list items ===")
for lst in inner_soup.find_all("div", class_="schedule__list")[:3]:
    print(str(lst)[:2000])
    print("---")

# Understand the sub-tab-content structure (which track does each belong to?)
print("\n\n=== sub-tab-contents in first day tab ===")
tabs = inner_soup.find_all("div", class_="tab")
first_tab = tabs[0]
schedule_div = first_tab.find("div", class_="schedule")
print(f"Schedule div has children:")
for i, child in enumerate(schedule_div.children):
    if hasattr(child, 'name') and child.name:
        classes = " ".join(child.get("class", []))
        if child.name == "input":
            print(f"  [{i}] input id={child.get('id')}")
        elif child.name == "label":
            print(f"  [{i}] label for={child.get('for')} txt='{child.get_text().strip()[:50]}'")
        elif child.name == "div":
            groups = child.find_all("div", class_="schedule__group", recursive=False)
            print(f"  [{i}] div cls='{classes}' groups={len(groups)}")
