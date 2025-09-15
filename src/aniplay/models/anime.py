from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Anime:
    id: Optional[int] = None
    name: str = ""
    path: str = ""
    cover_path: Optional[str] = None
    description: Optional[str] = None
    year: Optional[int] = None
    rating: float = 0.0
    status: str = "ongoing"
    mal_id: Optional[int] = None
    total_episodes: int = 0
    date_added: Optional[datetime] = None
    last_watched: Optional[datetime] = None
    is_favorite: bool = False
    episodes: List['Episode'] = None
    
    def __post_init__(self):
        if self.episodes is None:
            self.episodes = []