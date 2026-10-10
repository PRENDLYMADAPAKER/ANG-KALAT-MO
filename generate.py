import requests
import logging


def format_extinf(channel_id, tvg_id, tvg_chno, tvg_name, tvg_logo, group_title, display_name):
    """Formats the #EXTINF line."""
    # Ensure tvg_chno is empty if None or invalid
    chno_str = str(tvg_chno) if tvg_chno is not None and str(tvg_chno).isdigit() else ""

    # Basic sanitization for names/titles within the M3U format
    sanitized_tvg_name = tvg_name.replace("\"", "")
    sanitized_group_title = group_title.replace("\"", "")
    sanitized_display_name = display_name.replace(",", "")  # Commas break the EXTINF line itself

    return (f"#EXTINF:-1 "
            f"channel-id=\"{channel_id}\" "
            f"tvg-id=\"{tvg_id}\" "
            f"tvg-chno=\"\" "
            f"tvg-name=\"\" "
            f"tvg-logo=\"\" "
            f"group-title=\"\","
            f"{sanitized_display_name}\n")


def get_roku_stream_enhanced(channel_id):
    """Gets the stream URL for a Roku channel."""
    # Create a session to handle cookies
    session = requests.Session()
    
    # Add common headers to mimic a real browser
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://therokuchannel.roku.com",
        "Referer": "https://therokuchannel.roku.com/",
    })
    
    # Get CSRF token and playId to prepare playback request with enhanced headers
    try:
        csrf_response = session.get("https://therokuchannel.roku.com/api/v1/csrf")
        csrf_response.raise_for_status()
        csrf_token = csrf_response.json()["csrf"]

        content_url = f"https://therokuchannel.roku.com/api/v2/homescreen/content/https%3A%2F%2Fcontent.sr.roku.com%2Fcontent%2Fv1%2Froku-trc%2F{channel_id}%3Fexpand%3DviewOptions.channelId%252CviewOptions.playId%252Cnext.viewOptions.channelId%252Cnext.viewOptions.playId"
        content_response = session.get(content_url)
        content_response.raise_for_status()
        play_id = content_response.json()["viewOptions"][0]["playId"]

        headers = {
            "content-type": "application/json",
            "csrf-token": csrf_token,
        }
        
        data = {
            "rokuId": channel_id,
            "playId": play_id,
            "mediaFormat": "m3u",
            "drmType": "widevine",
            "quality": "fhd",
            "bifUrl": None,
            "adPolicyId": "",
            "providerId": "rokuavod"
        }

        # Make playback request
        playback_response = session.post(
            "https://therokuchannel.roku.com/api/v3/playback",
            headers=headers,
            json=data
        )
        
        if playback_response.status_code == 403:
            print(f"403 Forbidden Error - Response: {playback_response.text}")
            print("Troubleshooting steps:")
            print("1. Check if the channel_id is valid")
            print("2. The API might require authentication")
            print("3. The service might be blocking automated requests")
            return None
        
        playback_response.raise_for_status()
        playback_data = playback_response.json()

        # Transform the URL
        if "url" in playback_data:
            original_url = playback_data["url"]

            # Replace the domain and path as specified and remove all query parameters
            if "https://osm.sr.roku.com/osm/v1/hls/master/" in original_url:
                transformed_url = original_url.replace(
                    "https://osm.sr.roku.com/osm/v1/hls/master/",
                    "https://aka-live1050.delivery.roku.com/"
                ).replace("/live.m3u8", "/t2-origin/out/v1/live.m3u8")

                transformed_url = transformed_url.split('?')[0]
                
                return transformed_url
            else:
                print("URL format not recognized, returning original URL")
                return original_url
        else:
            print("No URL found in response")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except KeyError as e:
        print(f"Key error - missing expected data: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def fetch_url(url, is_json=True, is_gzipped=False):
    """Fetches URL content (placeholder implementation)."""
    # You'll need to implement this function based on your needs
    try:
        response = requests.get(url)
        response.raise_for_status()
        if is_json:
            return response.json()
        return response.text
    except Exception as e:
        logging.error(f"Error fetching URL {url}: {e}")
        return None


def write_m3u_file(filename, content):
    """Writes M3U content to file (placeholder implementation)."""
    # You'll need to implement this function based on your needs
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"Successfully wrote {filename}")
    except Exception as e:
        logging.error(f"Error writing file {filename}: {e}")


def generate_roku_playlist(sort="chno"):
    """Generates M3U playlist for Roku."""
    ROKU_URL = "https://i.mjh.nz/Roku/.channels.json" 
    EPG_URL = "https://github.com/matthuisman/i.mjh.nz/raw/master/Roku/all.xml"

    logging.info("--- Generating Roku playlist ---")
    data = fetch_url(ROKU_URL, is_json=True, is_gzipped=False)
    if not data or "channels" not in data:
        logging.error("Failed to fetch or parse Roku data.")
        return

    output_lines = [f"#EXTM3U url-tvg=\"{EPG_URL}\"\n"]
    channels_to_process = data.get("channels", {})

    # Sort channels
    try:
        if sort == "chno":
            sorted_channel_ids = sorted(channels_to_process.keys(), 
                                     key=lambda k: int(channels_to_process[k].get("chno", 99999)))
        else:  # Default to name sort
            sorted_channel_ids = sorted(channels_to_process.keys(), 
                                     key=lambda k: channels_to_process[k].get("name", "").lower())
    except Exception as e:
        logging.warning(f"Sorting failed for Roku, using default order. Error: {e}")
        sorted_channel_ids = list(channels_to_process.keys())

    # Build M3U entries
    for channel_id in sorted_channel_ids:
        channel = channels_to_process[channel_id]
        chno = channel.get("chno")
        name = channel.get("name", "Unknown Channel")
        logo = channel.get("logo", "")
        groups_list = channel.get("groups", [])
        group_title = groups_list[0] if groups_list else "Uncategorized"
        tvg_id = channel_id  # Roku IDs seem unique enough

        extinf = format_extinf(channel_id, tvg_id, chno, name, logo, group_title, name)
        stream_url = get_roku_stream_enhanced(channel_id)
        
        if stream_url:
            output_lines.append(extinf)
            output_lines.append(stream_url + "\n")

    write_m3u_file("roku.m3u", "".join(output_lines))


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_roku_playlist()
