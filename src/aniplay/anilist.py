from __future__ import annotations
import re
import requests
from pathlib import Path
from .cache import cover_path_for

ANILIST_ENDPOINT = "https://graphql.anilist.co"

QUERY = '''
query ($search: String) {
  Media(search: $search, type: ANIME) {
    id
    title { romaji english native }
    coverImage { extraLarge large medium color }
  }
}
'''

_session = requests.Session()
_session.headers.update({"User-Agent": "aniplay/0.1 (+https://github.com/youruser/aniplay)"})

_CLEAN_PATTERNS = [
    (r"\[[^\]]+\]", " "),
    (r"\([^\)]+\)", " "),
    (r"\b(480p|720p|1080p|2160p|x264|x265|10bit|8bit|HEVC|FLAC|AAC)\b", " "),
    (r"\bE(p|P)?\s?\d{1,3}\b", " "),
    (r"\bS\d{1,2}E\d{1,2}\b", " "),
    (r"_", " "),
]

def cleaned_title_from_filename(name: str) -> str:
    base = Path(name).stem
    s = base
    for pat, repl in _CLEAN_PATTERNS:
        s = re.sub(pat, repl, s, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s).strip(" -._")
    return s

def search_anime(title: str) -> dict | None:
    try:
        payload = {"query": QUERY, "variables": {"search": title}}
        r = _session.post(ANILIST_ENDPOINT, json=payload, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("data", {}).get("Media")
    except Exception:
        return None

def fetch_cover_and_title(raw_filename: str) -> tuple[str, Path | None]:
    q = cleaned_title_from_filename(raw_filename)
    media = search_anime(q)
    if not media:
        return (q, None)
    title = media["title"].get("english") or media["title"].get("romaji") or q
    cover_url = media["coverImage"].get("large") or media["coverImage"].get("medium")
    if not cover_url:
        return (title, None)
    dest = cover_path_for(cover_url)
    if not dest.exists():
        try:
            img = _session.get(cover_url, timeout=15)
            img.raise_for_status()
            dest.write_bytes(img.content)
        except Exception:
            return (title, None)
    return (title, dest)