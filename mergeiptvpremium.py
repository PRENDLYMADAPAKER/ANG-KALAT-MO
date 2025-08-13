import requests
from collections import defaultdict
import re
from datetime import datetime

# List of M3U source URLs
urls = [
    "http://drewlive24.duckdns.org:8081/Tims247.m3u8",
    "https://raw.githubusercontent.com/PRENDLYMADAPAKER/ANG-KALAT-MO/refs/heads/main/TheTVApp.m3u",
    "https://raw.githubusercontent.com/PRENDLYMADAPAKER/ANG-KALAT-MO/refs/heads/main/UDPTV.m3u"
]

# File where merged content will be saved
output_file = "IPTVPREMIUM.m3u"

# Track whether we've added the #EXTM3U header already
header_written = False

with open(output_file, "w", encoding="utf-8") as outfile:
    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
            lines = response.text.splitlines()

            for line in lines:
                # Skip header from other files
                if line.strip().startswith("#EXTM3U"):
                    if not header_written:
                        outfile.write(line + "\n")
                        header_written = True
                    continue
                outfile.write(line + "\n")
            print(f"✅ Downloaded and merged: {url}")
        except Exception as e:
            print(f"❌ Failed to fetch {url}: {e}")

print(f"\n🎉 Merge complete! Output saved to: {output_file}")
