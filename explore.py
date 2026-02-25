import re
from bs4 import BeautifulSoup

with open("https___se2026.inf.unibe.ch_en_program_schedule_.htm", encoding="utf-8") as f:
    outer_html = f.read()

outer_soup = BeautifulSoup(outer_html, "html.parser")
lines = outer_soup.find_all("span", id=re.compile(r"^line\d+$"))
print(f"Number of lines: {len(lines)}")

inner_lines = []
for span in lines:
    inner_lines.append(span.get_text())

inner_html = "\n".join(inner_lines)
print(f"Inner HTML length: {len(inner_html)} chars")

print("\n--- First 3000 chars of inner HTML ---")
print(inner_html[:3000])
