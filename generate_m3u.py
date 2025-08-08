import requests
import yaml

def main():
    # Load config
    try:
        with open("config.yml", "r") as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        print("❌ config.yml not found.")
        return
    except yaml.YAMLError as e:
        print(f"❌ Error parsing config.yml: {e}")
        return

    source_url = config.get("source")
    output_file = config.get("output", "playlist.m3u")

    if not source_url:
        print("❌ No source URL found in config.yml.")
        return

    # Download M3U content
    try:
        response = requests.get(source_url)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to download M3U file: {e}")
        return

    # Save to file
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"✅ M3U playlist saved to '{output_file}'")
    except Exception as e:
        print(f"❌ Failed to save file: {e}")

if __name__ == "__main__":
    main()
