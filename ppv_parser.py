import asyncio
import json
from pathlib import Path
from curl_cffi import requests

M3U8_FILE = "PPV_Streams.m3u"
API_URL = "https://api.ppv.to/api/streams"
BASE_URL = "https://ppv.to"

def build_stream_url(uri_name: str) -> str:
    if uri_name.startswith("http"):
        return uri_name
    clean_uri = uri_name.strip("/")
    return f"https://stream.ppv.to/live/{clean_uri}/index.m3u8"

async def main():
    print(f"🔄 Fetching data using impersonated browser profile from: {API_URL}")
    
    try:
        # impersonate="chrome" forces curl_cffi to match Google Chrome's TLS fingerprint exactly
        response = requests.get(
            API_URL, 
            impersonate="chrome",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Origin": BASE_URL,
                "Referer": f"{BASE_URL}/"
            },
            timeout=15.0
        )
        
        if response.status_code != 200:
            print(f"❌ API Error: HTTP {response.status_code}")
            return
        data = response.json()
    except Exception as e:
        print(f"❌ Failed to request API via impersonated profile: {e}")
        return

    if not data or not data.get("success"):
        print("❌ API reported unsuccessful response state.")
        return

    m3u_lines = []
    m3u_lines.append('#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_US1.xml.gz"')

    streams_added = 0
    categories = data.get("streams", [])

    for cat_block in categories:
        group_name = cat_block.get("category", "Live Events")
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
            
            # Append standard media player header properties to keep external connections alive
            final_url = f"{stream_link}|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36&Referer={BASE_URL}/&Origin={BASE_URL}"

            m3u_lines.append(f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group_name}",{display_title}')
            m3u_lines.append(final_url)
            streams_added += 1

    with open(M3U8_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))

    print(f"💾 Successfully generated {streams_added} fingerprint-bypassed streams inside {M3U8_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
    
