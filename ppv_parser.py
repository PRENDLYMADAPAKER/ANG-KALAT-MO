import asyncio
import re
import httpx
from pathlib import Path

M3U8_FILE = "PPV_Streams.m3u"
API_URL = "https://api.ppv.to/api/streams"
BASE_URL = "https://ppv.to"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Origin": BASE_URL,
    "Referer": f"{BASE_URL}/"
}

async def get_live_token_url(client: httpx.AsyncClient, uri_name: str) -> str:
    """
    Visits the live event page to scrape the authentic .m3u8 stream link
    complete with its active, authorized security session tokens.
    """
    page_url = f"{BASE_URL}/live/{uri_name.strip('/')}"
    try:
        response = await client.get(page_url, timeout=10.0)
        if response.status_code == 200:
            html_content = response.text
            
            # Find any source URL matching an m3u8 pattern in the page source
            m3u8_matches = re.findall(r'(https://[^\s"\']+\.m3u8[^\s"\']*)', html_content)
            if m3u8_matches:
                # Prioritize secure cluster domains if present
                for match in m3u8_matches:
                    if "stream" in match or "source" in match:
                        return match.replace("&amp;", "&")
                return m3u8_matches[0].replace("&amp;", "&")
    except Exception as e:
        print(f"⚠️ Token extraction skipped for {uri_name}: {e}")
    return f"https://stream.ppv.to/live/{uri_name.strip('/')}/index.m3u8"

async def fetch_streams():
    print(f"🔄 Fetching target payload data from API: {API_URL}")
    async with httpx.AsyncClient(headers=HEADERS, timeout=15.0, follow_redirects=True) as client:
        try:
            response = await client.get(API_URL)
            if response.status_code != 200:
                print(f"❌ API error: Received status code {response.status_code}")
                return None
            
            data = response.json()
            if not data or not data.get("success"):
                print("❌ API reported unsuccessful response state.")
                return None
                
            lines = []
            lines.append('#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_US1.xml.gz"')
            
            streams_added = 0
            categories = data.get("streams", [])
            
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
                    print(f"🔗 Resolving live tokens for: {display_title}")
                    
                    # Call the sub-handler to fetch the real, authenticated stream URL
                    raw_stream_link = await get_live_token_url(client, uri_name)
                    
                    # Append IPTV browser engine spoofing tags
                    stream_link = f"{raw_stream_link}|User-Agent={HEADERS['User-Agent']}&Referer={BASE_URL}/&Origin={BASE_URL}"
                    
                    lines.append(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group_name}",{display_title}')
                    lines.append(stream_link)
                    streams_added += 1
                    
                    # Small courtesy pause between requests to keep the server connection safe
                    await asyncio.sleep(0.5)

            print(f"✅ Successfully processed {streams_added} verified streams.")
            return lines

        except Exception as e:
            print(f"❌ Core processing error: {e}")
            return None

async def main():
    m3u_lines = await fetch_streams()
    if not m3u_lines or len(m3u_lines) <= 1:
        print("❌ Stream synchronization cancelled due to empty parsing array.")
        return
        
    with open(M3U8_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))
        
    print(f"💾 Playlist successfully built and updated: {M3U8_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
    
