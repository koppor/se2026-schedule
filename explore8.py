import re
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

with open("inner.html", encoding="utf-8") as f:
    inner_html = f.read()

inner_soup = BeautifulSoup(inner_html, "html.parser")

# Get all schedule groups - look at fields
all_groups = inner_soup.find_all("div", class_="schedule__group")
print(f"Total schedule groups: {len(all_groups)}")

# Examine the first 5 groups in detail
for i, grp in enumerate(all_groups[:5]):
    print(f"\n=== Group {i+1} ===")
    time_div = grp.find("div", class_="schedule__group-time")
    print(f"Time: {time_div.get_text().strip() if time_div else None}")
    
    desc = grp.find("div", class_="schedule__group-item-description")
    if desc:
        h1 = desc.find("h1")
        print(f"Title: {h1.get_text().strip() if h1 else None}")
        for p in desc.find_all("p", recursive=False):
            txt = p.get_text().strip().replace("\n", "  ")
            print(f"  p: {txt[:150]}")
    
    items_div = grp.find("div", class_="schedule__group-item-items")
    if items_div:
        items = items_div.find_all("div", class_="schedule__group-item-item")
        print(f"  Sub-items: {len(items)}")
        for item in items[:2]:
            print(f"    - {item.get_text().strip()[:100]}")

# Look at items that have sub-talks (paper sessions)
print("\n\n=== Groups with sub-items (sessions with papers) ===")
for grp in all_groups:
    items_div = grp.find("div", class_="schedule__group-item-items")
    if items_div:
        time_div = grp.find("div", class_="schedule__group-time")
        desc = grp.find("div", class_="schedule__group-item-description")
        h1 = desc.find("h1") if desc else None
        items = items_div.find_all("div", class_="schedule__group-item-item")
        print(f"\nTime: {time_div.get_text().strip()}, Title: {h1.get_text().strip() if h1 else None}, {len(items)} sub-items")
        
        # Look at a sub-item in detail
        for item in items[:1]:
            print(f"  Sub-item raw: {str(item)[:500]}")

# Check what speaker/person info looks like
print("\n\n=== Speaker/person paragraphs ===")
for grp in all_groups[:30]:
    desc = grp.find("div", class_="schedule__group-item-description")
    if desc:
        for p in desc.find_all("p"):
            txt = p.get_text().strip()
            if any(kw in txt for kw in ["Speaker:", "Author", "Organisation:", "Session Chair:"]):
                print(f"  {txt[:200]}")
