import os
import shutil
import requests
from PIL import Image
from io import BytesIO


def fetch_cover_from_anilist(series_name):
    """
    Fetch a cover image from AniList GraphQL API for the given series name.
    Returns PIL.Image or None if failed.
    """
    url = "https://graphql.anilist.co"
    query = """
    query ($search: String) {
      Media(search: $search, type: ANIME) {
        coverImage {
          large
        }
      }
    }
    """
    variables = {"search": series_name}
    try:
        resp = requests.post(url, json={"query": query, "variables": variables})
        resp.raise_for_status()
        data = resp.json()
        img_url = data["data"]["Media"]["coverImage"]["large"]
        img_resp = requests.get(img_url, stream=True)
        img_resp.raise_for_status()
        return Image.open(BytesIO(img_resp.content))
    except Exception as e:
        print(f"⚠️ Failed to fetch cover for {series_name}: {e}")
        return None


def precache_covers(library_path, covers_path, force_refetch=False):
    """
    Ensure covers exist for all series in library.
    If `force_refetch` is True, old covers are deleted and re-fetched.
    """
    os.makedirs(covers_path, exist_ok=True)

    series_folders = [
        d for d in os.listdir(library_path)
        if os.path.isdir(os.path.join(library_path, d))
    ]

    for name in series_folders:
        cover_file = os.path.join(covers_path, f"{name}.jpg")

        # Delete existing cover if refetching
        if force_refetch and os.path.exists(cover_file):
            try:
                os.remove(cover_file)
            except Exception:
                pass

        if not os.path.exists(cover_file):
            print(f"📥 Fetching cover for {name}...")
            img = fetch_cover_from_anilist(name)
            if img:
                try:
                    img = img.convert("RGB")  # ensure JPEG-compatible
                    img.save(cover_file, "JPEG", quality=85)
                    print(f"✅ Saved cover: {cover_file}")
                except Exception as e:
                    print(f"⚠️ Failed to save cover for {name}: {e}")
            else:
                print(f"⚠️ No cover found for {name}")


def ensure_episode_thumbnail(file_path, thumbs_path, seek="00:00:05", width=320):
    """
    Generate a thumbnail for a given episode video file using ffmpeg.
    Returns path to the thumbnail or None if failed.
    """
    os.makedirs(thumbs_path, exist_ok=True)

    import subprocess
    import hashlib

    # Use hash of file path for stable thumbnail filename
    file_hash = hashlib.md5(file_path.encode()).hexdigest()
    thumb_file = os.path.join(thumbs_path, f"{file_hash}.jpg")

    if not os.path.exists(thumb_file):
        try:
            cmd = [
                "ffmpeg",
                "-ss", seek,
                "-i", file_path,
                "-frames:v", "1",
                "-vf", f"scale={width}:-1",
                "-y",
                thumb_file,
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"⚠️ Failed to create thumbnail for {file_path}: {e}")
            return None

    return thumb_file
