import requests
from bs4 import BeautifulSoup
import json
import os

# Load the chapters JSON
with open("output/bhagavat_gita.json", "r", encoding="utf-8") as f:
    chapters = json.load(f)

# Ensure output folder exists
os.makedirs("output/chapters", exist_ok=True)

base_url = "https://vivekavani.com/b{chapter}v{verse}/"


def scrape_verse(chapter_num, verse_num):
    print("scraping chapter:", chapter_num, ":verse#", verse_num)
    url = base_url.format(chapter=chapter_num, verse=verse_num)
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"⚠️ Skipping {url} (status {resp.status_code})")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Example structure (you may need to tweak based on actual HTML)
    header = soup.find("header", class_="entry-header")
    verse_title = header.find("h1", class_="entry-title")
    entry_content = header.find_next("div", class_="entry-content")
    sanskrit = entry_content.find("p")
    transliteration = sanskrit.find_next("p")
    audio_tag = soup.find("audio")
    word_by_word_meaning = audio_tag.find_next("p")
    translation = word_by_word_meaning.find_next("p")
    commentary = translation.find_next("p")

    return {
        "verse_number": verse_num,
        "verse_title": verse_title.get_text(strip=True) if verse_title else None,
        "sanskrit": sanskrit.get_text(strip=True) if sanskrit else None,
        "transliteration": (
            transliteration.get_text(strip=True) if transliteration else None
        ),
        "word_by_word_meaning": (
            word_by_word_meaning.get_text(strip=True) if word_by_word_meaning else None
        ),
        "translation": translation.get_text(strip=True) if translation else None,
        "commentary": commentary.get_text(strip=True) if commentary else None,
        "audio": audio_tag["src"] if audio_tag and audio_tag.has_attr("src") else None,
        "source": url,
    }


for chapter in chapters:
    chapter_num = chapter["chapter_number"]
    verse_start = chapter["verse_start"]
    verse_end = chapter["verse_end"]

    print(f"📖 Scraping Chapter {chapter_num} ({verse_start}–{verse_end})")

    verses = []
    for v in range(verse_start, verse_end + 1):
        verse_data = scrape_verse(chapter_num, v)
        if verse_data:
            verses.append(verse_data)

    # Save JSON per chapter
    out_path = f"output/chapters/{chapter_num}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(verses, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved {out_path}")
