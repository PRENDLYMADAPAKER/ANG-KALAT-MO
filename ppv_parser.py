import asyncio
import json
import httpx
from pathlib import Path
from playwright.async_api import async_playwright

M3U8_FILE = "PPV_Streams.m3u"
API_URL = "https://api.ppv.to/api/streams"
BASE_URL = "https://ppv.to"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Accept": "application/json",
    "Origin": BASE_URL,
    "Referer": f"{BASE_URL}/"
}

async def fetch_api_data():
    print(f"🔄 Pulling stream metadata from API: {API_URL}")
    async with httpx.AsyncClient(headers=HEADERS, timeout=15.0) as client:
        try:
            response = await client.get(API_URL)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"❌ Failed to reach streams API: {e}")
    return None

async def capture_authenticated_stream(context, uri_name: str) -> str:
    """
    Launches a background page to let the player negotiate live authorization tokens,
    then captures the true authenticated streaming URL from network logs.
    """
    target_url = f"{BASE_URL}/live/{uri_name.strip('/')}"
    print(f"🎯 Sniffing network auth for: {target_url}")
    
    page = await context.new_page()
    detected_stream_url = None

    # Listen to all network responses triggered by the webpage player
    async def intercept_response(response):
        nonlocal detected_stream_url
        url = response.url
        # Capture the genuine streaming manifest once it obtains active authorization tokens
        if ".m3u8" in url and ("token=" in url or "expires=" in url or "sig=" in url or "stream" in url):
            if not detected_stream_url:
                detected_stream_url = url

    page.on("response", intercept_response)

    try:
        # Load the page and wait for the website's player components to initialize
        await page.goto(target_url, wait_until="domcontentloaded", timeout=15000)
        
        # Give the video player up to 5 seconds to run its security scripts and pull the video feed
        for _ in range(10):
            if detected_stream_url:
                break
            await asyncio.sleep(0.5)
    except Exception as e:
        print(f"⚠️ Network timeout or navigation block on event page: {e}")
    finally:
        await page.close()

    if detected_stream_url:
        print(f"✅ Found working authenticated stream link.")
        return detected_stream_url
    else:
        print(f"❌ Could not capture authorized tokens. Falling back to default structural path.")
        return f"https://stream.ppv.to/live/{uri_name.strip('/')}/index.m3u8"

async def main():
    api_data = await fetch_api_data()
    if not api_data or not api_data.get("success"):
        print("❌ Synchronization aborted: Invalid or empty API structure.")
        return

    m3u_lines = []
    m3u_lines.append('#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_US1.xml.gz"')

    categories = api_data.get("streams", [])
    
    # Initialize the background browser setup
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        # Emulate a clean desktop browser profile
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
            viewport={"width": 1280, "height": 720}
        )

        streams_processed = 0

        for cat_block in categories:
            group_name = cat_block.get("category", "PPV Events")
            event_list = cat_block.get("streams", [])

            for item in event_list:
                name = item.get("name", "Unknown Event")
                tag = item.get("tag", "")
                uri_name = item.get("uri_name")
                logo = item.get("poster", "")

                if not uri_name:
                    continue

                display_title = f"{name} ({tag})" if tag else name
                
                # Sniff out the link containing live session parameters
                live_m3u8 = await capture_authenticated_stream(context, uri_name)
                
                # Format the line with browser header spoofing commands for your IPTV app
                player_stream_link = f"{live_m3u8}|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0&Referer={BASE_URL}/&Origin={BASE_URL}"

                m3u_lines.append(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group_name}",{display_title}')
                m3u_lines.append(player_stream_link)
                streams_processed += 1
                
                print("-" * 40)

        await browser.close()

    if streams_processed > 0:
        with open(M3U8_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_lines))
        print(f"💾 Playlist built successfully with {streams_processed} live authenticated links: {M3U8_FILE}")
    else:
        print("❌ No active streams processed.")

if __name__ == "__main__":
    asyncio.run(main())
    
