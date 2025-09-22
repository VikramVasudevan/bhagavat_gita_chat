import requests
from bs4 import BeautifulSoup
import json
import re

url = "https://cdn.vivekavani.com/bg/"
resp = requests.get(url)
soup = BeautifulSoup(resp.text, "html.parser")

data = []

for chapter in soup.find_all("h2"):
    chapter_text = chapter.get_text(strip=True)
    m = re.match(r"Chapter\s+(\d+):\s+(.+)", chapter_text)
    if not m:
        continue
    chapter_num, chapter_title = m.groups()

    # First H3 = overview
    h3_overview = chapter.find_next("h3")
    if h3_overview:
        ol = h3_overview.find_next("ol")
        if ol:
            overview_items = [li.get_text(strip=True) for li in ol.find_all("li")]
    # Second H3 = verse range
    h3_range = h3_overview.find_next("h3") if h3_overview else None
    verse_start = verse_end = None
    if h3_range:
        verses_text = h3_range.get_text(strip=True)
        m2 = re.search(r"Verse[s]?\s+(\d+)\s+to\s+(\d+)", verses_text)
        if m2:
            verse_start, verse_end = map(int, m2.groups())

    # UL after second H3 = summary
    ul = h3_range.find_next("ul") if h3_range else None
    summary = [li.get_text(strip=True) for li in ul.find_all("li")] if ul else []

    data.append({
        "chapter_number": int(chapter_num),
        "chapter_title": chapter_title,
        "overview": overview_items,
        "verse_start": verse_start,
        "verse_end": verse_end,
        "summary": summary
    })

# Save JSON
with open("output/bhagavat_gita.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(json.dumps(data, indent=2, ensure_ascii=False))
