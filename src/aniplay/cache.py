from __future__ import annotations
from pathlib import Path
from hashlib import sha1
from appdirs import user_cache_dir


APP_NAME = "aniplay"
CACHE_DIR = Path(user_cache_dir(APP_NAME))
COVER_DIR = CACHE_DIR / "covers"
META_DIR = CACHE_DIR / "meta"


for p in (COVER_DIR, META_DIR):
    p.mkdir(parents=True, exist_ok=True)


def keyify(text: str) -> str:
    return sha1(text.encode("utf-8", errors="ignore")).hexdigest()


def cover_path_for(url_or_id: str, ext: str = ".jpg") -> Path:
    key = keyify(url_or_id)
    return COVER_DIR / f"{key}{ext}"