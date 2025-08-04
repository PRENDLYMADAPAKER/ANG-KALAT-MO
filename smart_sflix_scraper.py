import requests
import os
import re
import time
from bs4 import BeautifulSoup

# ===============================
# 🔧 CONFIGURATION
# ===============================
MOVIE_LIST_FILE = "movies.txt"
OUTPUT_M3U = "output/movies.m3u"
FAILED_LOG = "failed_movies.txt"
BATCH_SIZE = 20
DELAY_SECONDS = 2
SKIP_EXISTING = True
# ===============================

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Ensure output dir
os.makedirs(os.path.dirname(OUTPUT_M3U), exist_ok=True)

# Read movie list
with open(MOVIE_LIST_FILE, "r") as f:
    all_movies = [line.strip() for line in f if line.strip()]

# Skip already-added titles
existing_titles = set()
if SKIP_EXISTING and os.path.exists(OUTPUT_M3U):
    with open(OUTPUT_M3U, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#EXTINF"):
                existing_titles.add(line.strip().split(",")[-1])

# Get next batch
to_run = []
for title in all_movies:
    if title not in existing_titles:
        to_run.append(title)
    if len(to_run) == BATCH_SIZE:
        break

if not to_run:
    print("✅ All titles already processed.")
    exit()

# Write header if new
if not os.path.exists(OUTPUT_M3U):
    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

# Start scraping
for title in to_run:
    print(f"🎬 Processing: {title}")
    try:
        search_url = f"https://sflix.to/search/{title.replace(' ', '%20')}"
        search_res = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(search_res.text, "html.parser")

        first_result = soup.select_one("div.film-poster a")
        if not first_result:
            raise Exception("Not found")

        movie_href = first_result["href"]
        movie_page_url = f"https://sflix.to{movie_href}"

        movie_res = requests.get(movie_page_url, headers=headers, timeout=15)
        movie_soup = BeautifulSoup(movie_res.text, "html.parser")

        embed_frame = movie_soup.select_one("iframe")
        if not embed_frame:
            raise Exception("No iframe")

        embed_url = embed_frame["src"]
        if embed_url.startswith("//"):
            embed_url = "https:" + embed_url

        embed_res = requests.get(embed_url, headers=headers, timeout=15)
        m3u8_matches = re.findall(r'https://.*?\\.m3u8.*?"', embed_res.text)

        if not m3u8_matches:
            raise Exception("No .m3u8 link")

        stream_url = m3u8_matches[0].strip('"')

        with open(OUTPUT_M3U, "a", encoding="utf-8") as f:
            f.write(f"#EXTINF:-1,{title}\n{stream_url}\n")

        print(f"✅ Added: {title}")
    except Exception as e:
        print(f"❌ Failed: {title} — {e}")
        with open(FAILED_LOG, "a") as log:
            log.write(f"{title}\n")

    time.sleep(DELAY_SECONDS)

# ➕ Always add timestamp so Git sees it as changed
with open(OUTPUT_M3U, "a", encoding="utf-8") as f:
    f.write(f"# Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

print(f"\n📁 Playlist updated → {OUTPUT_M3U}")
