import asyncio
from playwright.async_api import async_playwright
import os
import time

# 🎬 Movie titles to search
MOVIE_TITLES = [
    "oppenheimer", "barbie", "the creator", "john wick chapter 4", "the flash"
]
OUTPUT_M3U = "output/movies.m3u"
DELAY_SECONDS = 5

async def fetch_stream_url(movie, page):
    try:
        await page.goto(f"https://sflix.to/search/{movie.replace(' ', '%20')}", timeout=60000)
        await page.wait_for_selector("div.film-poster a", timeout=10000)
        await page.click("div.film-poster a")
        await page.wait_for_selector("iframe", timeout=15000)
        iframe_element = await page.query_selector("iframe")
        embed_url = await iframe_element.get_attribute("src")
        if embed_url.startswith("//"):
            embed_url = "https:" + embed_url
        await page.goto(embed_url, timeout=60000)
        content = await page.content()
        start = content.find("https://")
        end = content.find(".m3u8", start)
        if start == -1 or end == -1:
            return None
        return content[start:end+5]
    except Exception as e:
        print(f"❌ Failed: {movie} — {str(e)}")
        return None

async def main():
    os.makedirs(os.path.dirname(OUTPUT_M3U), exist_ok=True)
    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for title in MOVIE_TITLES:
            print(f"🎬 Fetching: {title}")
            stream = await fetch_stream_url(title, page)
            if stream:
                with open(OUTPUT_M3U, "a", encoding="utf-8") as f:
                    f.write(f"#EXTINF:-1,{title}\n{stream}\n")
                print(f"✅ Added: {title}")
            else:
                print(f"❌ Skipped: {title}")
            await asyncio.sleep(DELAY_SECONDS)

        await browser.close()

    with open(OUTPUT_M3U, "a", encoding="utf-8") as f:
        f.write(f"# Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    print(f"📁 Done. Playlist saved to {OUTPUT_M3U}")

asyncio.run(main())
