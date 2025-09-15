from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Episode:
    id: Optional[int] = None
    anime_id: int = 0
    episode_number: int = 0
    title: Optional[str] = None
    file_path: str = ""
    duration: int = 0  # seconds
    thumbnail_path: Optional[str] = None
    date_added: Optional[datetime] = None
    progress_seconds: int = 0
    is_watched: bool = False
    last_watched: Optional[datetime] = None