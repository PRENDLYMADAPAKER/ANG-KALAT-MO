import requests
import os
import re
import time
from bs4 import BeautifulSoup

# ===============================
# 🔧 CONFIGURATION
# ===============================
MOVIE_TITLES = [
    "oppenheimer", "barbie", "the creator", "john wick chapter 4", "the flash"
]
OUTPUT_M3U = "output/movies.m3u"
BATCH_SIZE = 20
DELAY_SECONDS = 5
# ===============================

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Ensure output directory
os.makedirs(os.path.dirname(OUTPUT_M3U), exist_ok=True)

# Prepare or load existing M3U content
existing_titles = set()
if os.path.exists(OUTPUT_M3U):
    with open(OUTPUT_M3U, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#EXTINF"):
                existing_titles.add(line.strip().split(",")[-1])
else:
    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

# Process movies
added = 0
for title in MOVIE_TITLES:
    if title in existing_titles:
        continue
    print(f"🎬 Fetching: {title}")

    try:
        search_url = f"https://sflix.to/search/{title.replace(' ', '%20')}"
        search_res = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(search_res.text, "html.parser")
        result = soup.select_one("div.film-poster a")
        if not result:
            raise Exception("Movie not found")

        movie_url = f"https://sflix.to{result['href']}"
        movie_page = requests.get(movie_url, headers=headers, timeout=15)
        movie_soup = BeautifulSoup(movie_page.text, "html.parser")
        embed = movie_soup.select_one("iframe")
        if not embed:
            raise Exception("No embed iframe")

        embed_url = "https:" + embed["src"] if embed["src"].startswith("//") else embed["src"]
        embed_res = requests.get(embed_url, headers=headers, timeout=15)
        m3u8_match = re.findall(r'https://.*?\.m3u8.*?"', embed_res.text)
        if not m3u8_match:
            raise Exception("No m3u8 found")

        stream_url = m3u8_match[0].strip('"')
        with open(OUTPUT_M3U, "a", encoding="utf-8") as f:
            f.write(f"#EXTINF:-1,{title}\n{stream_url}\n")

        added += 1
        print(f"✅ Added: {title}")
        time.sleep(DELAY_SECONDS)

    except Exception as e:
        print(f"❌ Failed: {title} — {e}")

# Force change detection
with open(OUTPUT_M3U, "a", encoding="utf-8") as f:
    f.write(f"# Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

print(f"\n📁 Done. {added} movie(s) added to {OUTPUT_M3U}")
