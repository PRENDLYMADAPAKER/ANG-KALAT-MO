import asyncio
from playwright.async_api import async_playwright
import aiohttp
from datetime import datetime

API_URL = "https://api.ppv.to/api/streams"

# Corrected inline option string architecture for perfect IPTV player ingestion
STREAM_BYPASS_TAGS = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0&Referer=https://veplay.top/&Origin=https://veplay.top"

ALLOWED_CATEGORIES = {
    "24/7 Streams", "Wrestling", "Football", "Basketball", "Baseball",
    "Combat Sports", "Motorsports", "Miscellaneous", "Boxing", "Darts"
}

CATEGORY_LOGOS = {
    "24/7 Streams": "http://drewlive24.duckdns.org:9000/Logos/247.png",
    "Wrestling": "http://drewlive24.duckdns.org:9000/Logos/Wrestling.png",
    "Football": "http://drewlive24.duckdns.org:9000/Logos/Soccer2.png",
    "Basketball": "http://drewlive24.duckdns.org:9000/Logos/Basketball-2.png",
    "Baseball": "http://drewlive24.duckdns.org:9000/Logos/Baseball.png",
    "Combat Sports": "http://drewlive24.duckdns.org:9000/Logos/Boxing.png",
    "Motorsports": "http://drewlive24.duckdns.org:9000/Logos/F12.png",
    "Miscellaneous": "http://drewlive24.duckdns.org:9000/Logos/247.png",
    "Boxing": "http://drewlive24.duckdns.org:9000/Logos/Boxing.png",
    "Darts": "http://drewlive24.duckdns.org:9000/Logos/Darts.png"
}

CATEGORY_TVG_IDS = {
    "24/7 Streams": "24.7.Dummy.us",
    "Football": "Soccer.Dummy.us",
    "Wrestling": "PPV.EVENTS.Dummy.us",
    "Combat Sports": "PPV.EVENTS.Dummy.us",
    "Baseball": "MLB.Baseball.Dummy.us",
    "Basketball": "Basketball.Dummy.us",
    "Motorsports": "Racing.Dummy.us",
    "Miscellaneous": "PPV.EVENTS.Dummy.us",
    "Boxing": "PPV.EVENTS.Dummy.us",
    "Darts": "Darts.Dummy.us"
}

GROUP_RENAME_MAP = {
    "24/7 Streams": "PPVLand - Live Channels 24/7",
    "Wrestling": "PPVLand - Wrestling Events",
    "Football": "PPVLand - Global Football Streams",
    "Basketball": "PPVLand - Basketball Hub",
    "Baseball": "PPVLand - Baseball Action HD",
    "Combat Sports": "PPVLand - MMA & Fight Nights",
    "Motorsports": "PPVLand - Motorsport Live",
    "Miscellaneous": "PPVLand - Random Events",
    "Boxing": "PPVLand - Boxing",
    "Darts": "PPVLand - Darts"
}

async def check_m3u8_url(session, url):
    """Verifies that the intercepted stream link actually serves video segments."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": "https://veplay.top/",
            "Origin": "https://veplay.top"
        }
        async with session.get(url, headers=headers, timeout=8) as resp:
            return resp.status == 200
    except:
        return False

async def get_streams():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(API_URL) as resp:
            resp.raise_for_status()
            return await resp.json()

async def grab_single_stream(context, stream_item, session, url_map):
    """Worker task that opens and processes an independent channel window asynchronously."""
    name = stream_item["name"]
    iframe_url = stream_item["iframe"]
    cat = stream_item["category"]
    unique_key = f"{name}::{cat}::{iframe_url}"
    
    page = await context.new_page()
    found_streams = set()

    # Log any stream manifests matching media formats
    def intercept_media(response):
        if ".m3u8" in response.url:
            found_streams.add(response.url)

    page.on("response", intercept_media)
    print(f"📡 Sniffing network for: {name}")

    try:
        await page.goto(iframe_url, wait_until="domcontentloaded", timeout=20000)
        await asyncio.sleep(2.5)

        # Smart Element Interaction: Target video players directly instead of basic canvas clicking
        player_selectors = ["div#player", "video", "div.jwplayer", ".play-button", "body"]
        clicked = False
        for selector in player_selectors:
            try:
                target = page.locator(selector).first
                if await target.is_visible():
                    await target.click(timeout=2000)
                    clicked = True
                    break
            except:
                continue
                
        if not clicked:
            # Fallback coordinate click if selectors fail
            await page.mouse.click(640, 360)

        # Allow time for keys and segment files to generate
        await asyncio.sleep(4.5)
    except Exception as e:
        print(f"⚠️ Navigation block encountered on '{name}': {e}")
    finally:
        page.remove_listener("response", intercept_media)
        await page.close()

    # Validate active links
    valid_links = []
    for link in found_streams:
        if await check_m3u8_url(session, link):
            valid_links.append(link)

    if valid_links:
        print(f"✅ Success: Found working connection stream for [{name}]")
        url_map[unique_key] = valid_links
    else:
        print(f"❌ Failed to extract valid streams for [{name}]")

def build_m3u(streams, url_map):
    lines = ['#EXTM3U url-tvg="https://tinyurl.com/DrewLive002-epg"']
    seen_names = set()

    for s in streams:
        name_lower = s["name"].strip().lower()
        if name_lower in seen_names:
            continue
        seen_names.add(name_lower)

        unique_key = f"{s['name']}::{s['category']}::{s['iframe']}"
        urls = url_map.get(unique_key, [])

        if not urls:
            continue

        orig_category = s["category"].strip()
        final_group = GROUP_RENAME_MAP.get(orig_category, orig_category)
        logo = CATEGORY_LOGOS.get(orig_category, "")
        tvg_id = CATEGORY_TVG_IDS.get(orig_category, "Sports.Dummy.us")

        # Select the primary authenticated playlist link
        chosen_url = urls[0]
        
        # Attach the bypass parameters right to the link so players bypass protections cleanly
        player_ready_url = f"{chosen_url}{STREAM_BYPASS_TAGS}"

        lines.append(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-logo="{logo}" group-title="{final_group}",{s["name"]}')
        lines.append(player_ready_url)

    return "\n".join(lines)

async def main():
    try:
        data = await get_streams()
    except Exception as e:
        print(f"❌ Fatal: Failed to download source stream array structural definition: {e}")
        return

    raw_streams = []
    for category in data.get("streams", []):
        cat = category.get("category", "").strip()
        if cat not in ALLOWED_CATEGORIES:
            continue
        for stream in category.get("streams", []):
            iframe = stream.get("iframe")
            name = stream.get("name", "Unnamed Event")
            if iframe:
                raw_streams.append({"name": name, "iframe": iframe, "category": cat})

    # Deduplicate matches
    seen_names = set()
    streams = []
    for s in raw_streams:
        name_key = s["name"].strip().lower()
        if name_key not in seen_names:
            seen_names.add(name_key)
            streams.append(s)

    if not streams:
        print("🚫 No active matches available across tracked parameters.")
        return

    print(f"🚀 Loaded {len(streams)} targets. Starting batch network sniffing sequence...")

    url_map = {}
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        
        # Limit worker concurrency to 3 profiles at a time to prevent CPU throttling on GitHub
        semaphore = asyncio.BoundedSemaphore(3)
        
        async with aiohttp.ClientSession() as session:
            async def worker(stream_item):
                async with semaphore:
                    await grab_single_stream(context, stream_item, session, url_map)

            # Fire off concurrent tracking calls
            await asyncio.gather(*(worker(s) for s in streams))
            
        await browser.close()

    print("\n💾 Formatting and assembling final M3U playlist file data...")
    playlist_content = build_m3u(streams, url_map)
    
    with open("PPVLand.m3u8", "w", encoding="utf-8") as f:
        f.write(playlist_content)

    print(f"✅ Operations complete. Output stored successfully inside PPVLand.m3u8.")

if __name__ == "__main__":
    asyncio.run(main())
        
