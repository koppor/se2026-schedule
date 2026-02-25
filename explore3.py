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

# Find schedule structure - look for article, section, or specific class patterns
print("=== Looking for time patterns ===")
time_pattern = re.compile(r'\d{1,2}:\d{2}\s*[–\-]\s*\d{1,2}:\d{2}')
all_text = inner_soup.get_text()
times = time_pattern.findall(all_text)
print(f"Found {len(times)} time ranges")
for t in times[:30]:
    print(f"  {t}")

print("\n=== Looking for checkbox/radio inputs ===")
inputs = inner_soup.find_all("input")
for inp in inputs[:30]:
    print(f"  type={inp.get('type')} id={inp.get('id')} name={inp.get('name')}")

print("\n=== Looking for article/section tags ===")
articles = inner_soup.find_all("article")
print(f"Found {len(articles)} articles")
sections = inner_soup.find_all("section")
print(f"Found {len(sections)} sections")

# Try to find schedule entries - look for divs with typical schedule classes
print("\n=== Div classes containing 'schedule' or 'event' or 'slot' or 'session' ===")
for div in inner_soup.find_all("div"):
    classes = " ".join(div.get("class", []))
    if any(kw in classes.lower() for kw in ["schedule", "event", "slot", "session", "entry", "talk", "item"]):
        txt = div.get_text()[:100].replace("\n", " ").strip()
        print(f"  .{classes}: {txt}")
