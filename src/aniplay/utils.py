from __future__ import annotations
from pathlib import Path


def human_readable_path(p: Path) -> str:
try:
return str(p)
except Exception:
return p.as_posix()