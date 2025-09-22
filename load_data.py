from tqdm import tqdm
import os
import json
import chromadb
from openai import OpenAI
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# Initialize Chroma client
client = chromadb.PersistentClient(path="chromadb_store")
collection_name = "bhagavat_gita"

if collection_name in [c.name for c in client.list_collections()]:
    collection = client.get_collection(name=collection_name)
else:
    collection = client.create_collection(name=collection_name)

# OpenAI client (ensure OPENAI_API_KEY is set in env)
openai_client = OpenAI()

input_dir = "output/chapters_final"
embedding_cache_file = "output/embeddings.json"
os.makedirs("output", exist_ok=True)

# Load existing embeddings cache if exists
if os.path.exists(embedding_cache_file):
    with open(embedding_cache_file, "r", encoding="utf-8") as f:
        embedding_cache = json.load(f)
else:
    embedding_cache = {}

def get_embedding(text):
    """Compute or reuse embedding"""
    if text in embedding_cache:
        return embedding_cache[text]
    response = openai_client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    embedding = response.data[0].embedding
    embedding_cache[text] = embedding
    return embedding

global_index = 0

for fname in sorted(os.listdir(input_dir), key=lambda f: int(f.split(".")[0])):
    if not fname.endswith(".json"):
        continue

    chapter_number = int(fname.split(".")[0])
    with open(os.path.join(input_dir, fname), "r", encoding="utf-8") as f:
        verses = json.load(f)

    for verse in tqdm(verses):
        global_index += 1

        text_to_embed = []

        # Add translation
        for i, t in enumerate(verse.get("translation", []), 1):
            text_to_embed.append(f"Translation {i}:\n{t}")

        # Add commentary
        for i, c in enumerate(verse.get("commentary", []), 1):
            text_to_embed.append(f"Commentary {i}:\n{c}")

        # Add word-by-word meaning
        wbw = verse.get("word_by_word_meaning", "")
        if wbw:
            text_to_embed.append(f"Word by Word Meaning:\n{wbw}")

        # Combine into a single string for embedding
        text_to_embed_str = "\n\n".join(text_to_embed)

        embedding_vector = get_embedding(text_to_embed_str)

        metadata = {
            "chapter_number": chapter_number,
            "chapter_title": verse.get("chapter_title"),
            "verse_number": verse.get("verse_number"),
            "verse_title": verse.get("verse_title"),
            "sanskrit": verse.get("sanskrit"),
            "transliteration": verse.get("transliteration"),
            "word_by_word_meaning": verse.get("word_by_word_meaning"),
            "translation": "\n".join(verse.get("translation")),
            "commentary": "\n".join(verse.get("commentary")),
            "audio": verse.get("audio"),
            "source": verse.get("source"),
            "_global_index": global_index,
        }

        # print("metadata = ", metadata)
        collection.add(
            documents=[text_to_embed_str],
            embeddings=[embedding_vector],
            metadatas=[metadata],
            ids=[f"b{chapter_number}v{verse['verse_number']}"]
        )

    print(f"✅ Loaded chapter {chapter_number} into Chroma DB")

# Save embeddings cache
with open(embedding_cache_file, "w", encoding="utf-8") as f:
    json.dump(embedding_cache, f)

print(f"✅ Embeddings saved to {embedding_cache_file}")
