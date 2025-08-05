import asyncio
from playwright.async_api import async_playwright
import os

OUTPUT_FILE = "output/movies.m3u"
MOVIE_LIST_FILE = "movies.txt"
BASE_URL = "https://sflix.to"

async def get_movie_url(page, title):
    search_url = f"{BASE_URL}/search/{title.replace(' ', '%20')}"
    await page.goto(search_url, timeout=60000)

    try:
        await page.wait_for_selector("a[href*='/movie/']", timeout=30000)
        elements = await page.query_selector_all("a[href*='/movie/']")
        if not elements:
            return None
        first = elements[0]
        href = await first.get_attribute("href")
        return BASE_URL + href
    except Exception as e:
        print(f"⚠️ Selector failed for {title}: {e}")
        return None

async def save_m3u(links):
    os.makedirs("output", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for title, link in links.items():
            f.write(f"#EXTINF:-1,{title}\n{link}\n")
    print(f"✅ Saved {len(links)} entries to {OUTPUT_FILE}")

async def main():
    movie_links = {}
    with open(MOVIE_LIST_FILE, "r") as f:
        movie_titles = [line.strip() for line in f if line.strip()]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        for title in movie_titles:
            print(f"🎬 Fetching: {title}")
            url = await get_movie_url(page, title)
            if url:
                movie_links[title] = url
                print(f"✅ Found: {url}")
            else:
                print(f"❌ Failed: {title}")
            await asyncio.sleep(5)

        await browser.close()

    await save_m3u(movie_links)

if __name__ == "__main__":
    asyncio.run(main())
