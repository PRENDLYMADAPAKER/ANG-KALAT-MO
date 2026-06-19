import asyncio
import json
import httpx
from pathlib import Path

M3U8_FILE = "PPV_Streams.m3u"
API_URL = "https://api.ppv.to/api/streams"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Gecko/20100101) Firefox/130.0",
    "Accept": "application/json",
    "Origin": "https://ppv.to",
    "Referer": "https://ppv.to/"
}

def build_stream_url(uri_name: str) -> str:
    if uri_name.startswith("http"):
        return uri_name
        
    clean_uri = uri_name.strip("/")
    base_stream = f"https://stream.ppv.to/live/{clean_uri}/index.m3u8"
    
    # 🌟 THE SECRET SOLUTION: Inject strict browser identity parameters directly into the playlist stream URL
    # This works perfectly on players like TiviMate, Televizo, OTT Navigator, and Perfect Player.
    bypass_headers = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0&Referer=https://ppv.to/&Origin=https://ppv.to"
    
    return f"{base_stream}{bypass_headers}"

async def fetch_streams():
    print(f"🔄 Fetching data from API: {API_URL}")
    async with httpx.AsyncClient(headers=HEADERS, timeout=15.0) as client:
        try:
            response = await client.get(API_URL)
            if response.status_code != 200:
                print(f"❌ API error: Received HTTP status code {response.status_code}")
                return None
            return response.json()
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None

def build_m3u_content(data) -> list:
    lines = []
    lines.append('#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_US1.xml.gz"')
    
    if not data or not data.get("success"):
        print("❌ API reported unsuccessful response state.")
        return lines

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
            stream_link = build_stream_url(uri_name)
            
            lines.append(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group_name}",{display_title}')
            lines.append(stream_link)
            streams_added += 1

    print(f"✅ Processed metadata rows. Generated {streams_added} active streams.")
    return lines

async def main():
    data = await fetch_streams()
    if not data:
        print("❌ Stream structural synchronization aborted.")
        return
        
    m3u_lines = build_m3u_content(data)
    
    with open(M3U8_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))
        
    print(f"💾 Playlist successfully updated: {M3U8_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
            
