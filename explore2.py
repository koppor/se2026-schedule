import re
from bs4 import BeautifulSoup

with open("https___se2026.inf.unibe.ch_en_program_schedule_.htm", encoding="utf-8") as f:
    outer_html = f.read()

outer_soup = BeautifulSoup(outer_html, "html.parser")
lines = outer_soup.find_all("span", id=re.compile(r"^line\d+$"))
inner_lines = [span.get_text() for span in lines]
inner_html = "\n".join(inner_lines)

inner_soup = BeautifulSoup(inner_html, "html.parser")

# Find schedule structure
print("=== Top-level divs with class info ===")
for div in inner_soup.find_all("div", class_=True, limit=50):
    classes = " ".join(div.get("class", []))
    txt = div.get_text()[:80].replace("\n", " ").strip()
    print(f"  .{classes}: {txt}")

print("\n=== Looking for time patterns ===")
time_pattern = re.compile(r'\d{1,2}:\d{2}\s*[–-]\s*\d{1,2}:\d{2}')
all_text = inner_soup.get_text()
times = time_pattern.findall(all_text)
print(f"Found {len(times)} time ranges")
for t in times[:20]:
    print(f"  {t}")
