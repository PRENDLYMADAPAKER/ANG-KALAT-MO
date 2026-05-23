import requests
import re
from playwright.sync_api import sync_playwright

# ==========================================
# 1. CONFIGURATION
# ==========================================
EVENTS_URL = "https://api.cdnlivetv.tv/api/v1/events/sports/?user=cdnlivetv&plan=free"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
SPOOF_IP = "77.238.79.111"

HEADERS = {
    "Accept": "application/json",
    "Origin": "https://streamsports99.su",
    "Referer": "https://streamsports99.su/",
    "User-Agent": USER_AGENT
}

TARGET_SPORTS = ["Soccer", "Cricket", "Fight", "WWE"]

# ==========================================
# 2. HIGH-SPEED PLAYLIST GENERATOR
# ==========================================
def build_playlist():
    print("[*] Fetching Sports Events API...")
    try:
        resp = requests.get(EVENTS_URL, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            print(f"[-] Failed to fetch API. Status: {resp.status_code}")
            return
        sports_categories = resp.json().get("cdn-live-tv", {})
    except Exception as e:
        print(f"[-] Error fetching API: {e}")
        return

    print("[*] Starting Playwright Browser (Blitz Mode)...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True, 
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security']
        )
        
        context = browser.new_context(
            user_agent=USER_AGENT,
            extra_http_headers={
                "Referer": "https://streamsports99.su/",
                "Origin": "https://streamsports99.su"
            }
        )
        
        page = context.new_page()
        
        # Block images/css/fonts so the page loads instantly
        page.route("**/*", lambda route: 
            route.abort() if route.request.resource_type in ["image", "media", "font", "stylesheet"] 
            else route.continue_()
        )
        
        with open("liveevents.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            channel_id = 1
            
            for sport, events in sports_categories.items():
                if sport not in TARGET_SPORTS or not isinstance(events, list):
                    continue
                    
                for event in events:
                    if event.get("status") != "live":
                        continue 
                    
                    match_name = f"[{sport}] {event.get('homeTeam', event.get('event', 'Live'))} vs {event.get('awayTeam', '')}"
                    logo = event.get("homeTeamIMG", event.get("eventIMG", ""))
                    
                    for ch in event.get("channels", []):
                        ch_name = ch.get("channel_name", "Stream")
                        player_url = ch.get("url")
                        
                        if not player_url:
                            continue
                            
                        print(f"-> Blitzing: {match_name} ({ch_name})")
                        
                        try:
                            # Wait exactly for the m3u8 request to fire, fail instantly if it takes longer than 3 seconds
                            with page.expect_request(re.compile(r"\.m3u8"), timeout=3000) as m3u8_req:
                                page.goto(player_url)
                            
                            # Grab the URL the millisecond it generates
                            final_url = m3u8_req.value.url
                            
                            f.write(f'#EXTINF:-1 tvg-chno="{channel_id}" tvg-id="{sport}.{channel_id}" tvg-name="{match_name} ({ch_name})" tvg-logo="{logo}" group-title="{sport}",{match_name} ({ch_name})\n')
                            f.write(f'#EXTVLCOPT:http-referrer={player_url}\n')
                            f.write(f'#EXTVLCOPT:http-origin={player_url}\n')
                            f.write(f'#EXTVLCOPT:http-user-agent={USER_AGENT}\n')
                            f.write(f'{final_url}|x-forwarded-for:{SPOOF_IP}\n\n')
                            
                            channel_id += 1
                            print(f"  [+] Snagged it.")
                            
                        except Exception:
                            # If it hits the 3-second timeout, it skips and moves on with zero hesitation
                            print(f"  [-] Missed it. Moving on.")
                        
        browser.close()
        print("\n[+] Finished! Saved to 'liveevents.m3u'")

if __name__ == "__main__":
    build_playlist()
