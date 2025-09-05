import os
import subprocess
import hashlib
import requests

ANILIST_URL = "https://graphql.anilist.co"
QUERY = """
query ($search: String) {
  Media(search: $search, type: ANIME) {
    title { romaji }
    coverImage { large }
  }
}
"""

def precache_covers(library_path="library", cache_dir="covers"):
    os.makedirs(library_path, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)

    if not os.path.isdir(library_path):
        return

    series_folders = [
        d for d in os.listdir(library_path)
        if os.path.isdir(os.path.join(library_path, d))
    ]

    for series in series_folders:
        target = os.path.join(cache_dir, f"{series}.jpg")
        if os.path.exists(target):
            continue
        try:
            variables = {"search": series}
            r = requests.post(ANILIST_URL, json={"query": QUERY, "variables": variables}, timeout=12)
            r.raise_for_status()
            media = r.json().get("data", {}).get("Media")
            if not media:
                continue
            img_url = media["coverImage"]["large"]
            img = requests.get(img_url, timeout=12)
            img.raise_for_status()
            with open(target, "wb") as f:
                f.write(img.content)
            print(f"Cached cover: {series}")
        except Exception as e:
            print(f"Cover fetch failed for '{series}': {e}")

def _hash_path(path: str) -> str:
    return hashlib.sha1(path.encode("utf-8")).hexdigest()

def ensure_episode_thumbnail(video_path: str, cache_dir: str, seek="00:00:10", width=320) -> str or None:
    """
    Create (or return) a cached jpg thumbnail for the given video using ffmpeg.
    Returns the thumbnail path or None on failure.
    """
    os.makedirs(cache_dir, exist_ok=True)
    base = _hash_path(video_path)  # avoid illegal filename chars
    thumb_path = os.path.join(cache_dir, base + ".jpg")
    if os.path.exists(thumb_path):
        return thumb_path
    try:
        # Generate a frame at `seek` time
        subprocess.run(
            ["ffmpeg", "-y", "-ss", seek, "-i", video_path, "-frames:v", "1", "-vf", f"scale={width}:-2", thumb_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )
        return thumb_path if os.path.exists(thumb_path) else None
    except Exception:
        return None
