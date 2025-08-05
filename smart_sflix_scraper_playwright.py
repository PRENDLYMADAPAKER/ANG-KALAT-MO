# ✅ PATCHED smart_sflix_scraper_playwright.py (now reads from movies.txt)
# - Loads dynamic list of movies from movies.txt
# - Still appends to output/movies.m3u
# - Debug HTML dump on failure

import asyncio
from playwright.async_api import async_playwright
import os
import time

MOVIE_LIST_FILE = "movies.txt"
OUTPUT_M3U = "output/movies.m3u"
DELAY_SECONDS = 5

async def fetch_stream_url(movie, page):
    try:
        print(f"\n🎬 Fetching: {movie}")
        await page.goto(f"https://sflix.to/search/{movie.replace(' ', '%20')}", timeout=60000)
        await page.wait_for_selector("div.film-poster a", timeout=10000)
        await page.click("div.film-poster a")
        await page.wait_for_selector("iframe", timeout=15000)

        iframe = await page.query_selector("iframe")
        embed_url = await iframe.get_attribute("src")
        if embed_url.startswith("//"):
            embed_url = "https:" + embed_url

        await page.goto(embed_url, timeout=60000)
        await page.wait_for_timeout(5000)
        html = await page.content()
        start = html.find("https://")
        end = html.find(".m3u8", start)
        if start == -1 or end == -1:
            raise ValueError(".m3u8 not found")
        return html[start:end+5]

    except Exception as e:
        print(f"❌ Failed: {movie} – {e}")
        with open(f"output/{movie.replace(' ', '_')}_debug.html", "w", encoding="utf-8") as f:
            f.write(await page.content())
        return None

async def main():
    os.makedirs("output", exist_ok=True)

    # Load movie titles from movies.txt
    if not os.path.exists(MOVIE_LIST_FILE):
        print(f"⚠️ {MOVIE_LIST_FILE} not found.")
        return

    with open(MOVIE_LIST_FILE, "r", encoding="utf-8") as f:
        MOVIE_TITLES = [line.strip() for line in f if line.strip()]

    if not MOVIE_TITLES:
        print("⚠️ No movies found in movies.txt.")
        return

    if not os.path.exists(OUTPUT_M3U):
        with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for title in MOVIE_TITLES:
            stream = await fetch_stream_url(title, page)
            if stream:
                with open(OUTPUT_M3U, "a", encoding="utf-8") as f:
                    f.write(f"#EXTINF:-1,{title}\n{stream}\n")
                print(f"✅ Added: {title}")
            else:
                print(f"⚠️ Skipped: {title}")
            await asyncio.sleep(DELAY_SECONDS)

        await browser.close()

    with open(OUTPUT_M3U, "a", encoding="utf-8") as f:
        f.write(f"# Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    print(f"\n✅ Done. Playlist saved to {OUTPUT_M3U}")

asyncio.run(main())
        
