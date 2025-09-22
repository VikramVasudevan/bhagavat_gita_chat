import os
import re
import json

input_dir = "output/chapters"
output_dir = "output/chapters_final"
os.makedirs(output_dir, exist_ok=True)

# Load chapter metadata for lookup
with open("output/bhagavat_gita.json", "r", encoding="utf-8") as f:
    chapters_metadata = json.load(f)
chapter_lookup = {c["chapter_number"]: c["chapter_title"] for c in chapters_metadata}
print("chapter_lookup = ", chapter_lookup)
global_counter = 1  # overall verse position across all chapters

def split_combined_entry(entry, chapter_num):
    results = []

    # Try to detect range in verse title (e.g., "Verse 4-6")
    m = re.search(r"Verse\s+(\d+)(?:\s*-\s*(\d+))?", entry.get("verse_title", ""))
    if m:
        start = int(m.group(1))
        end = int(m.group(2)) if m.group(2) else start
    else:
        # fallback: use existing verse_number
        start = end = entry.get("verse_number", 1)

    verse_count = end - start + 1

    for i, v in enumerate(range(start, end + 1)):
        new_entry = entry.copy()

        # Relative verse number
        new_entry["relative_verse_number"] = v

        # Chapter info from filename
        new_entry["chapter_number"] = chapter_num
        new_entry["chapter_title"] = chapter_lookup.get(chapter_num, "")

        # Update verse title
        new_entry["verse_title"] = f"Bhagavad Gita: Chapter {chapter_num}, Verse {v}"

        # ⚠️ Split sanskrit by markers like "|| 4||"
        if entry.get("sanskrit"):
            parts = re.split(r"(\|\|\s*\d+\s*\|\|)", entry["sanskrit"])
            combined_parts = []
            for j in range(0, len(parts), 2):
                text = parts[j].strip()
                marker = parts[j + 1].strip() if j + 1 < len(parts) else ""
                combined_parts.append((text + " " + marker).strip())
            if len(combined_parts) >= verse_count:
                new_entry["sanskrit"] = combined_parts[i]

        # ⚠️ Split transliteration by numbers (best-effort)
        if entry.get("transliteration"):
            parts = re.split(r"(\d+)", entry["transliteration"])
            parts = [p.strip() for p in parts if p.strip()]
            if len(parts) >= verse_count:
                new_entry["transliteration"] = parts[i]

        # Translation & commentary are arrays; duplicate for safety
        if isinstance(entry.get("translation"), list):
            new_entry["translation"] = entry["translation"][:]
        if isinstance(entry.get("commentary"), list):
            new_entry["commentary"] = entry["commentary"][:]

        results.append(new_entry)

    return results


# Sort files numerically by chapter
json_files = [f for f in os.listdir(input_dir) if f.endswith(".json")]
def chapter_sort_key(fname):
    m = re.match(r"(\d+)\.json", fname)
    return int(m.group(1)) if m else float('inf')

for fname in sorted(json_files, key=chapter_sort_key):
    chapter_num = int(re.match(r"(\d+)\.json", fname).group(1))  # extract chapter from filename
    in_path = os.path.join(input_dir, fname)
    with open(in_path, "r", encoding="utf-8") as f:
        verses = json.load(f)

    final_verses = []
    for entry in verses:
        split_verses = split_combined_entry(entry, chapter_num)
        for sv in split_verses:
            sv["_global_index"] = global_counter
            global_counter += 1
        final_verses.extend(split_verses)

    out_path = os.path.join(output_dir, fname)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_verses, f, indent=2, ensure_ascii=False)

    print(f"✅ Processed {fname} → {out_path}")
