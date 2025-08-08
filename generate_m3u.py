import requests

def main():
    source_url = "https://doxm3u8.netlify.app/"
    output_file = "playlist.m3u"

    print(f"🔁 Downloading playlist from: {source_url}")

    try:
        response = requests.get(source_url)
        response.raise_for_status()

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(response.text)

        print(f"✅ Playlist saved as: {output_file}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
