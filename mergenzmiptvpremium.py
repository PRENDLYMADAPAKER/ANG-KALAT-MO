import requests

# List of M3U source URLs
urls = [
    "https://raw.githubusercontent.com/PRENDLYMADAPAKER/ANG-KALAT-MO/refs/heads/main/IPTV%20PREMIUM",
    "https://raw.githubusercontent.com/BuddyChewChew/My-Streams/refs/heads/main/tv.m3u",
    "https://raw.githubusercontent.com/insa-ship-it/app-m3u-generator/refs/heads/main/playlists/roku_all.m3u",
    "https://raw.githubusercontent.com/PRENDLYMADAPAKER/ANG-KALAT-MO/refs/heads/main/playlists/plutotv_all.m3u",
    "https://raw.githubusercontent.com/BuddyChewChew/RakutenTV/refs/heads/main/playlist.m3u"
]

# EPG URLs with spaces after commas to satisfy your IPTV player
EPG_URL = "https://epgshare01.online/epgshare01/epg_ripper_PH1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_PH2.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_ID1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_MY1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_HK1.xml.gz, https://epgshare01.online/epgshare01/epg_ripper_US1.xml.gz, https://raw.githubusercontent.com/dbghelp/mewatch-EPG/refs/heads/main/mewatch.xml, https://raw.githubusercontent.com/BuddyChewChew/RakutenTV/main/epg.xml, https://raw.githubusercontent.com/doms9/iptv/refs/heads/default/M3U8/TV.xml"

output_file = "NZMIPTVPREMIUM.m3u"

with open(output_file, "w", encoding="utf-8") as outfile:
    # Write the custom header containing the spaced out EPG list
    outfile.write(f'#EXTM3U x-tvg-url="{EPG_URL}"\n')

    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
            lines = response.text.splitlines()

            for line in lines:
                # Skip the headers inside the downloaded M3U files
                if line.strip().startswith("#EXTM3U"):
                    continue
                
                outfile.write(line + "\n")
                
            print(f"✅ Downloaded and merged: {url}")
        except Exception as e:
            print(f"❌ Failed to fetch {url}: {e}")

print(f"\n🎉 Merge complete! Output saved to: {output_file}")
