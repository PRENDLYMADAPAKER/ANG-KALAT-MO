# anime_247_generator.py
# ✅ Generates anime_247.m3u with working (live) anime 24/7 streams

import os
import requests
from datetime import datetime

OUTPUT_FILE = "output/anime_247.m3u"
TIMEOUT = 5  # seconds

STREAMS = [
    {"tvg_id": "DBZ24", "group_title": "Anime", "channel_name": "Dragon Ball Z 24/7", "url": "http://178.33.132.162:1935/live/dragonballz.stream/playlist.m3u8"},
    {"tvg_id": "Naruto24", "group_title": "Anime", "channel_name": "Naruto Shippuden 24/7", "url": "http://usa1.iptv2022.com:8080/anime/naruto24/playlist.m3u8"},
    {"tvg_id": "OnePiece24", "group_title": "Anime", "channel_name": "One Piece 24/7", "url": "http://freeviewanime.ddns.net:8000/stream/onepiece.m3u8"},
    {"tvg_id": "Bleach24", "group_title": "Anime", "channel_name": "Bleach 24/7", "url": "http://iptvanime.net:8080/bleach/stream.m3u8"},
    {"tvg_id": "AOT24", "group_title": "Anime", "channel_name": "Attack on Titan 24/7", "url": "http://animeworld.stream/aot/playlist.m3u8"},
    {"tvg_id": "MHA24", "group_title": "Anime", "channel_name": "My Hero Academia 24/7", "url": "http://stream.animecloud.live/mha/index.m3u8"},
    {"tvg_id": "PokemonClassic", "group_title": "Anime", "channel_name": "Pokemon Classic 24/7", "url": "http://live.poketv.to/classic/stream.m3u8"},
    {"tvg_id": "PokemonXYZ", "group_title": "Anime", "channel_name": "Pokemon XYZ 24/7", "url": "http://live.poketv.to/xyz/stream.m3u8"},
    {"tvg_id": "DeathNote", "group_title": "Anime", "channel_name": "Death Note 24/7", "url": "http://animevibes.live/dn/playlist.m3u8"},
    {"tvg_id": "TokyoGhoul", "group_title": "Anime", "channel_name": "Tokyo Ghoul 24/7", "url": "http://animetv.stream/tokyoghoul/live.m3u8"},
    {"tvg_id": "ToonamiLoop", "group_title": "Anime", "channel_name": "Toonami (Loop)", "url": "http://freeviewanime.ddns.net:8000/stream/toonami.m3u8"},
    {"tvg_id": "Inuyasha", "group_title": "Anime", "channel_name": "Inuyasha 24/7", "url": "http://otakustream.tv/inuyasha.m3u8"},
    {"tvg_id": "FairyTail", "group_title": "Anime", "channel_name": "Fairy Tail 24/7", "url": "http://animehub.ddns.net:8000/fairytail/stream.m3u8"},
    {"tvg_id": "SailorMoon", "group_title": "Anime", "channel_name": "Sailor Moon 24/7", "url": "http://retroanime.ddns.net:8000/sailormoon.m3u8"},
    {"tvg_id": "CodeGeass", "group_title": "Anime", "channel_name": "Code Geass 24/7", "url": "http://animerush.live/codegeass/index.m3u8"},
    {"tvg_id": "DemonSlayer", "group_title": "Anime", "channel_name": "Demon Slayer 24/7", "url": "http://animestream.to/demonslayer/live.m3u8"},
    {"tvg_id": "BlackClover", "group_title": "Anime", "channel_name": "Black Clover 24/7", "url": "http://animefox.tv/blackclover/stream.m3u8"},
    {"tvg_id": "Boruto", "group_title": "Anime", "channel_name": "Boruto 24/7", "url": "http://narutostreams.to/boruto/playlist.m3u8"},
    {"tvg_id": "Digimon", "group_title": "Anime", "channel_name": "Digimon Adventure 24/7", "url": "http://digistream.to/adventure/index.m3u8"},
    {"tvg_id": "Gintama", "group_title": "Anime", "channel_name": "Gintama 24/7", "url": "http://animeclassic.to/gintama/stream.m3u8"},
    {"tvg_id": "YuYuHakusho", "group_title": "Anime", "channel_name": "Yu Yu Hakusho 24/7", "url": "http://animezone.live/yuyuhakusho.m3u8"},
    {"tvg_id": "DBSuper", "group_title": "Anime", "channel_name": "Dragon Ball Super 24/7", "url": "http://dbzchannel.live/dbsuper/index.m3u8"},
    {"tvg_id": "Trigun", "group_title": "Anime", "channel_name": "Trigun 24/7", "url": "http://animehits.to/trigun/playlist.m3u8"},
    {"tvg_id": "Fullmetal", "group_title": "Anime", "channel_name": "Fullmetal Alchemist 24/7", "url": "http://stream.animehero.tv/fullmetal.m3u8"},
    {"tvg_id": "HunterXHunter", "group_title": "Anime", "channel_name": "Hunter x Hunter 24/7", "url": "http://hxhchannel.net/live.m3u8"}
]

def is_live(url):
    try:
        r = requests.head(url, timeout=TIMEOUT, allow_redirects=True)
        return r.status_code == 200
    except Exception:
        return False

def generate_playlist():
    os.makedirs("output", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        live_count = 0
        for stream in STREAMS:
            if is_live(stream["url"]):
                f.write(f'#EXTINF:-1 tvg-id="{stream["tvg_id"]}" group-title="{stream["group_title"]}", {stream["channel_name"]}\n')
                f.write(f'{stream["url"]}\n')
                live_count += 1
        f.write(f"# Updated: {datetime.utcnow().isoformat()}\n")
    print(f"✅ Saved {live_count} live channels to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_playlist()
