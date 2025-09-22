import os
import re
import json

input_dir = "output/chapters"
output_dir = "output/chapters_final"
os.makedirs(output_dir, exist_ok=True)

def split_combined_entry(entry):
    results = []

    # detect range in verse title (e.g., "Verse 4-6")
    m = re.search(r"Verse\s+(\d+)(?:\s*-\s*(\d+))?", entry.get("verse_title", ""))
    if not m:
        return [entry]  # no split needed

    start = int(m.group(1))
    end = int(m.group(2)) if m.group(2) else start

    # split into individual verses
    for v in range(start, end + 1):
        new_entry = entry.copy()
        new_entry["verse_number"] = v
        new_entry["verse_title"] = f"Bhagavad Gita: Chapter {entry['verse_number']}, Verse {v}"

        # ⚠️ Optionally: split text by "|| X||" markers
        if entry.get("sanskrit"):
            parts = re.split(r"\|\|\s*\d+\s*\|\|", entry["sanskrit"])
            if len(parts) >= (end - start + 1):
                new_entry["sanskrit"] = parts[v - start].strip()

        if entry.get("transliteration"):
            parts = re.split(r"(\d+\s*)", entry["transliteration"])
            # fallback: keep full transliteration if splitting fails
            if len(parts) > (end - start):
                new_entry["transliteration"] = parts[v - start].strip()

        # Keep same translation/commentary/audio if not splittable
        results.append(new_entry)

    return results

for fname in os.listdir(input_dir):
    if not fname.endswith(".json"):
        continue

    with open(os.path.join(input_dir, fname), "r", encoding="utf-8") as f:
        verses = json.load(f)

    final_verses = []
    for entry in verses:
        final_verses.extend(split_combined_entry(entry))

    # save per chapter
    out_path = os.path.join(output_dir, fname)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_verses, f, indent=2, ensure_ascii=False)

    print(f"✅ Processed {fname} → {out_path}")
