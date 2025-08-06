# anime_247_generator.py
import os
import random
from datetime import datetime

OUTPUT_FILE = "output/anime_247.m3u"
os.makedirs("output", exist_ok=True)

anime_streams = [
    {"title": "Black Clover 24/7", "url": "http://animefox.tv/blackclover/stream.m3u8", "tvg": "BlackClover"},
    {"title": "Naruto Shippuden 24/7", "url": "http://161.97.123.52:8080/anime/naruto/playlist.m3u8", "tvg": "Naruto"},
    {"title": "One Piece 24/7", "url": "http://198.251.81.236:8080/live/OnePiece/stream.m3u8", "tvg": "OnePiece"},
    {"title": "Dragon Ball Z 24/7", "url": "http://178.33.132.162:1935/live/dragonballz.stream/playlist.m3u8", "tvg": "DBZ"},
    {"title": "Attack on Titan 24/7", "url": "http://51.81.208.167:8080/aot/live.m3u8", "tvg": "AOT"},
    {"title": "Demon Slayer 24/7", "url": "http://103.145.12.56:8080/demonslayer/live.m3u8", "tvg": "DemonSlayer"},
    {"title": "Bleach 24/7", "url": "http://198.251.81.236:8080/live/Bleach/stream.m3u8", "tvg": "Bleach"},
    {"title": "Tokyo Ghoul 24/7", "url": "http://animevibes.live/tokyoghoul/playlist.m3u8", "tvg": "TokyoGhoul"},
    {"title": "My Hero Academia 24/7", "url": "http://animefox.tv/mha/stream.m3u8", "tvg": "MHA"},
    {"title": "Jujutsu Kaisen 24/7", "url": "http://iptvanime.net:8000/jujutsukaisen/stream.m3u8", "tvg": "JJK"},
    {"title": "Fairy Tail 24/7", "url": "http://198.251.81.236:8080/live/FairyTail/stream.m3u8", "tvg": "FairyTail"},
    {"title": "Code Geass 24/7", "url": "http://198.251.81.236:8080/live/CodeGeass/stream.m3u8", "tvg": "CodeGeass"},
    {"title": "Digimon 24/7", "url": "http://live.animetv.online/digimon.m3u8", "tvg": "Digimon"},
    {"title": "Pokemon Classic 24/7", "url": "http://live.poketv.to/classic/stream.m3u8", "tvg": "PokemonClassic"},
    {"title": "Inuyasha 24/7", "url": "http://animefox.tv/inuyasha/stream.m3u8", "tvg": "Inuyasha"},
    {"title": "Death Note 24/7", "url": "http://198.251.81.236:8080/live/DeathNote/stream.m3u8", "tvg": "DeathNote"},
    {"title": "Chainsaw Man 24/7", "url": "http://animehero.tv/chainsawman/stream.m3u8", "tvg": "ChainsawMan"},
    {"title": "Gintama 24/7", "url": "http://otakustream.to/gintama/stream.m3u8", "tvg": "Gintama"},
    {"title": "Yu Yu Hakusho 24/7", "url": "http://animetv.stream/yuyu/stream.m3u8", "tvg": "YuYuHakusho"},
    {"title": "Toonami Loop", "url": "http://freeviewanime.ddns.net:8000/stream/toonami.m3u8", "tvg": "Toonami"}
]

random.shuffle(anime_streams)
selected = anime_streams[:random.randint(10, len(anime_streams))]

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for stream in selected:
        f.write(f'#EXTINF:-1 tvg-id="{stream["tvg"]}" group-title="Anime", {stream["title"]}\n')
        f.write(f'{stream["url"]}\n')
    f.write(f"# Updated: {datetime.utcnow().isoformat()}Z\n")

print(f"✅ Saved {len(selected)} anime streams to {OUTPUT_FILE}")
