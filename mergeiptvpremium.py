import requests
from collections import defaultdict
import re
from datetime import datetime

playlist_urls = [
    "https://raw.githubusercontent.com/PRENDLYMADAPAKER/ANG-KALAT-MO/refs/heads/main/TheTVApp.m3u",
    "https://raw.githubusercontent.com/PRENDLYMADAPAKER/ANG-KALAT-MO/refs/heads/main/UDPTV.m3u"
]

UDPTV_URL = "https://raw.githubusercontent.com/PRENDLYMADAPAKER/ANG-KALAT-MO/refs/heads/main/UDPTV.m3u"
EPG_URL = "https://tinyurl.com/DrewLive002-epg"
OUTPUT_FILE = "IPTV PREMIUM.m3u"
REMOVED_FILE = "Removed_NSFW.m3u8"

def fetch_playlist(url):
    print(f"Fetching: {url}")
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        return res.content.decode('utf-8', errors='ignore').strip().splitlines()
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return []

def extract_timestamp_from_udptv(lines):
    for line in lines:
        if line.strip().startswith("# Last forced update:"):
            print(f"✅ Found UDPTV timestamp: {line.strip()}")
            return line.strip()
    print("⚠️ No update timestamp found in UDPTV.")
    return None

def parse_playlist(lines, source_url="Unknown"):
    parsed = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF:"):
            extinf = line
            headers = []
            i += 1
            while i < len(lines) and lines[i].strip().startswith("#") and not lines[i].strip().startswith("#EXTINF:"):
                headers.append(lines[i].strip())
                i += 1
            if i < len(lines) and lines[i].strip() and not lines[i].strip().startswith("#"):
                url = lines[i].strip()
                parsed.append((extinf, tuple(headers), url))
                i += 1
            else:
                print(f"⚠️ Skipped invalid channel in {source_url}")
        else:
            i += 1
    print(f"✅ Parsed {len(parsed)} channels from {source_url}")
    return parsed

def is_nsfw(extinf, headers, url):
    nsfw_keywords = ['nsfw', 'xxx', 'porn']
    extinf_lower = extinf.lower()
    headers_lower = ' '.join(headers).lower()
    url_lower = url.lower()
    group_match = re.search(r'group-title="([^"]+)"', extinf_lower)
    if group_match:
        group_title = group_match.group(1)
        if any(k in group_title for k in nsfw_keywords):
            return True
    combined_text = f"{extinf_lower} {headers_lower} {url_lower}"
    return any(k in combined_text for k in nsfw_keywords)

def write_merged_playlist(all_channels, timestamp_line):
    lines = [f'#EXTM3U url-tvg="{EPG_URL}"']
    if timestamp_line:
        lines.append(timestamp_line)
    lines.append("")

    sortable = []
    for extinf, headers, url in all_channels:
        group_match = re.search(r'group-title="([^"]+)"', extinf)
        group = group_match.group(1) if group_match else "Other"
        title_match = re.search(r',([^,]+)$', extinf)
        title = title_match.group(1).strip() if title_match else ""
        sortable.append((group.lower(), title.lower(), group, extinf, headers, url))

    sorted_channels = sorted(sortable)

    current_group = None
    count = 0

    for _, _, group_name, extinf, headers, url in sorted_channels:
        if group_name != current_group:
            if current_group is not None:
                lines.append("")
            lines.append(f"#EXTGRP:{group_name}")
            current_group = group_name
        lines.append(extinf)
        lines.extend(headers)
        lines.append(url)
        count += 1

    if lines and lines[-1] == "":
        lines.pop()

    final_output = '\n'.join(lines) + '\n'

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(final_output)

    print(f"\n✅ Wrote {count} clean channels to {OUTPUT_FILE} ({len(final_output.splitlines())} lines).")

def write_removed_channels(nsfw_channels):
    if not nsfw_channels:
        return
    with open(REMOVED_FILE, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for extinf, headers, url in nsfw_channels:
            f.write(extinf + "\n")
            for h in headers:
                f.write(h + "\n")
            f.write(url + "\n\n")
    print(f"🗑️ Logged {len(nsfw_channels)} removed NSFW/XXX/Porn entries to {REMOVED_FILE}")

if __name__ == "__main__":
    print(f"🚀 Starting merge: {datetime.now()}\n")

    all_channels = set()
    timestamp_line = None

    # Process UDPTV first
    print(f"--- Processing UDPTV: {UDPTV_URL} ---")
    udptv_lines = fetch_playlist(UDPTV_URL)
    timestamp_line = extract_timestamp_from_udptv(udptv_lines)
    all_channels.update(parse_playlist(udptv_lines, UDPTV_URL))

    # Process remaining playlists
    print(f"\n--- Processing other playlists ---")
    for url in playlist_urls:
        if url == UDPTV_URL:
            continue
        lines = fetch_playlist(url)
        all_channels.update(parse_playlist(lines, url))

    # Filter and separate NSFW content
    nsfw_channels = [entry for entry in all_channels if is_nsfw(*entry)]
    clean_channels = [entry for entry in all_channels if not is_nsfw(*entry)]

    write_removed_channels(nsfw_channels)
    write_merged_playlist(clean_channels, timestamp_line)

    print(f"\n✅ Merge complete: {datetime.now()}")
