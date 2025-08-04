import requests
import os

# Configuration (was in config.yml)
sources = {
    "IPTV_Org_Movies": "https://iptv-org.github.io/iptv/categories/movies.m3u",
    "Curated_VOD": "https://raw.githubusercontent.com/jromero88/iptv/master/VOD.m3u"
}

output_path = "./output/combined_movies.m3u"

# Fetch and combine
combined_playlist = []

for name, url in sources.items():
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            print(f"✅ Fetched {name} ({len(r.text.splitlines())} lines)")
            combined_playlist.append(r.text)
        else:
            print(f"❌ Failed to fetch {name}: HTTP {r.status_code}")
    except Exception as e:
        print(f"❌ Error fetching {name}: {e}")

# Save combined M3U
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(combined_playlist))

print(f"📁 Combined M3U saved to: {output_path}")
