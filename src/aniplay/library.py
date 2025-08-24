from __future__ import annotations
from pathlib import Path
from typing import Iterable, List


VIDEO_EXTS = {".mkv", ".mp4", ".avi", ".mov", ".m4v"}


class Episode:
def __init__(self, path: Path):
self.path = path
self.title_hint = path.name


def __repr__(self) -> str:
return f"Episode({self.path!s})"


def iter_episodes(paths: Iterable[Path]) -> List[Episode]:
eps: List[Episode] = []
for root in paths:
if not root.exists():
continue
if root.is_file() and root.suffix.lower() in VIDEO_EXTS:
eps.append(Episode(root))
continue
for p in root.rglob("*"):
if p.is_file() and p.suffix.lower() in VIDEO_EXTS:
eps.append(Episode(p))
eps.sort(key=lambda e: (str(e.path.parent).lower(), e.path.name.lower()))
return eps