#!/usr/bin/env python3
"""
Library Scanner - Scans filesystem and populates database
File: src/aniplay/core/library_scanner.py
"""

import os
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import subprocess
import json
from datetime import datetime

from .database import DatabaseManager
from ..models.anime import Anime
from ..models.episode import Episode
from ..utils.file_utils import get_video_files, get_video_duration, natural_sort_key

class LibraryScanner:
    """Scans library directories and populates the database with anime and episodes"""
    
    # Common video extensions
    VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.webm', '.m4v', '.flv', '.wmv'}
    
    # Episode number patterns (ordered by specificity)
    EPISODE_PATTERNS = [
        r'[Ee]pisode[\s\-_]*(\d+)',           # Episode 01, episode-01, episode_01
        r'[Ee]p[\s\-_]*(\d+)',                # Ep 01, ep-01, ep_01
        r'[\[\(](\d+)[\]\)]',                 # [01], (01)
        r'[\s\-_](\d+)[\s\-_]',               # -01-, _01_, space-01-space
        r'^(\d+)[\s\-_]',                     # 01-title, 01_title, 01 title
        r'[\s\-_](\d+)$',                     # title-01, title_01, title 01
        r'[\s\-_](\d+)\.',                    # title-01.ext, title_01.ext
        r'[Ss](\d+)[Ee](\d+)',                # S1E01 format (season/episode)
    ]
    
    def __init__(self, db_manager: DatabaseManager, covers_path: str, thumbs_path: str):
        self.db = db_manager
        self.covers_path = covers_path
        self.thumbs_path = thumbs_path
        
        # Ensure directories exist
        os.makedirs(covers_path, exist_ok=True)
        os.makedirs(thumbs_path, exist_ok=True)
    
    def scan_library(self, library_path: str, update_existing: bool = False) -> Dict[str, int]:
        """
        Scan the library directory and populate the database
        
        Args:
            library_path: Path to the anime library
            update_existing: Whether to update existing entries
            
        Returns:
            Dict with scan statistics: {'anime_added': 0, 'episodes_added': 0, 'errors': 0}
        """
        stats = {'anime_added': 0, 'episodes_added': 0, 'updated': 0, 'errors': 0}
        
        if not os.path.exists(library_path):
            raise FileNotFoundError(f"Library path does not exist: {library_path}")
        
        print(f"Scanning library: {library_path}")
        
        # Get existing anime to avoid duplicates
        existing_anime = {anime.name: anime for anime in self.db.get_all_anime()}
        
        # Scan each anime directory
        for item in os.listdir(library_path):
            anime_path = os.path.join(library_path, item)
            
            if not os.path.isdir(anime_path):
                continue
                
            try:
                if item in existing_anime and not update_existing:
                    print(f"Skipping existing: {item}")
                    continue
                
                result = self._scan_anime_directory(anime_path, item, existing_anime.get(item))
                
                if result:
                    if result['is_new']:
                        stats['anime_added'] += 1
                    else:
                        stats['updated'] += 1
                    stats['episodes_added'] += result['episodes_added']
                    
            except Exception as e:
                print(f"Error scanning {item}: {e}")
                stats['errors'] += 1
        
        print(f"Scan complete: {stats}")
        return stats
    
    def _scan_anime_directory(self, anime_path: str, anime_name: str, existing_anime: Optional[Anime] = None) -> Optional[Dict]:
        """Scan a single anime directory"""
        print(f"Processing: {anime_name}")
        
        # Get video files
        video_files = self._get_video_files(anime_path)
        if not video_files:
            print(f"  No video files found in {anime_name}")
            return None
        
        # Parse episodes
        episodes_data = self._parse_episodes(video_files, anime_path)
        if not episodes_data:
            print(f"  Could not parse episodes for {anime_name}")
            return None
        
        # Create or update anime entry
        if existing_anime:
            anime_id = existing_anime.id
            is_new = False
            # Update total_episodes if changed
            if existing_anime.total_episodes != len(episodes_data):
                self.db._update_anime_episodes_count(anime_id, len(episodes_data))
        else:
            # Create new anime entry
            anime = Anime(
                name=anime_name,
                path=anime_path,
                cover_path=self._get_cover_path(anime_name),
                total_episodes=len(episodes_data),
                date_added=datetime.now()
            )
            anime_id = self.db.add_anime(anime)
            is_new = True
        
        # Add episodes
        episodes_added = 0
        existing_episodes = {ep.file_path: ep for ep in self.db.get_episodes(anime_id)} if not is_new else {}
        
        for ep_data in episodes_data:
            if ep_data['file_path'] not in existing_episodes:
                episode = Episode(
                    anime_id=anime_id,
                    episode_number=ep_data['episode_number'],
                    title=ep_data['title'],
                    file_path=ep_data['file_path'],
                    duration=ep_data.get('duration', 0),
                    thumbnail_path=ep_data.get('thumbnail_path')
                )
                self.db.add_episode(episode)
                episodes_added += 1
        
        return {
            'is_new': is_new,
            'episodes_added': episodes_added
        }
    
    def _get_video_files(self, directory: str) -> List[str]:
        """Get all video files in a directory"""
        video_files = []
        
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(file.lower())
                if ext in self.VIDEO_EXTENSIONS:
                    video_files.append(file_path)
        
        # Natural sort (handles numbers properly)
        return sorted(video_files, key=lambda x: natural_sort_key(os.path.basename(x)))
    
    def _parse_episodes(self, video_files: List[str], anime_path: str) -> List[Dict]:
        """Parse episode information from video files"""
        episodes = []
        
        for i, file_path in enumerate(video_files):
            filename = os.path.basename(file_path)
            name_without_ext = os.path.splitext(filename)[0]
            
            # Extract episode number
            episode_number = self._extract_episode_number(filename)
            if episode_number is None:
                episode_number = i + 1  # Fallback to file order
            
            # Generate episode title (clean filename)
            title = self._generate_episode_title(name_without_ext, episode_number)
            
            # Get video duration
            duration = self._get_video_duration(file_path)
            
            # Generate thumbnail path (will be created later if needed)
            thumbnail_path = self._get_thumbnail_path(file_path)
            
            episodes.append({
                'episode_number': episode_number,
                'title': title,
                'file_path': file_path,
                'duration': duration,
                'thumbnail_path': thumbnail_path
            })
        
        # Sort by episode number
        episodes.sort(key=lambda x: x['episode_number'])
        return episodes
    
    def _extract_episode_number(self, filename: str) -> Optional[int]:
        """Extract episode number from filename using regex patterns"""
        for pattern in self.EPISODE_PATTERNS:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                try:
                    # Handle S1E01 format (use episode number, ignore season)
                    if len(match.groups()) == 2:
                        return int(match.group(2))
                    else:
                        return int(match.group(1))
                except (ValueError, IndexError):
                    continue
        return None
    
    def _generate_episode_title(self, filename: str, episode_number: int) -> str:
        """Generate a clean episode title from filename"""
        title = filename
        
        # Remove episode number patterns
        for pattern in self.EPISODE_PATTERNS:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        # Clean up common patterns
        title = re.sub(r'[\[\(\{].*?[\]\)\}]', '', title)  # Remove bracketed content
        title = re.sub(r'[-_\.]+', ' ', title)             # Replace separators with spaces
        title = re.sub(r'\s+', ' ', title)                 # Collapse multiple spaces
        title = title.strip()
        
        # If title is empty or too short, use episode number
        if not title or len(title) < 3:
            title = f"Episode {episode_number}"
        
        return title
    
    def _get_video_duration(self, file_path: str) -> int:
        """Get video duration in seconds using ffprobe"""
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', file_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                duration = float(data.get('format', {}).get('duration', 0))
                return int(duration)
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, 
                json.JSONDecodeError, ValueError, FileNotFoundError):
            pass
        
        return 0
    
    def _get_cover_path(self, anime_name: str) -> str:
        """Get the cover image path for an anime"""
        cover_path = os.path.join(self.covers_path, f"{anime_name}.jpg")
        return cover_path if os.path.exists(cover_path) else None
    
    def _get_thumbnail_path(self, video_path: str) -> str:
        """Generate thumbnail path for a video file"""
        filename = os.path.basename(video_path)
        name_without_ext = os.path.splitext(filename)[0]
        thumb_filename = f"{name_without_ext}.jpg"
        return os.path.join(self.thumbs_path, thumb_filename)
    
    def rescan_anime(self, anime_name: str, library_path: str) -> bool:
        """Rescan a specific anime directory"""
        anime_path = os.path.join(library_path, anime_name)
        if not os.path.exists(anime_path):
            return False
        
        # Get existing anime
        existing_anime = None
        for anime in self.db.get_all_anime():
            if anime.name == anime_name:
                existing_anime = anime
                break
        
        try:
            result = self._scan_anime_directory(anime_path, anime_name, existing_anime)
            return result is not None
        except Exception as e:
            print(f"Error rescanning {anime_name}: {e}")
            return False
    
    def clean_orphaned_entries(self, library_path: str) -> int:
        """Remove database entries for anime/episodes that no longer exist on disk"""
        removed_count = 0
        
        for anime in self.db.get_all_anime():
            if not os.path.exists(anime.path):
                print(f"Removing orphaned anime: {anime.name}")
                self.db._remove_anime(anime.id)
                removed_count += 1
                continue
            
            # Check episodes
            for episode in self.db.get_episodes(anime.id):
                if not os.path.exists(episode.file_path):
                    print(f"Removing orphaned episode: {episode.file_path}")
                    self.db._remove_episode(episode.id)
                    removed_count += 1
        
        return removed_count


# Additional database methods needed (add to DatabaseManager class)
class DatabaseManagerExtensions:
    """Additional methods to add to DatabaseManager"""
    
    def _update_anime_episodes_count(self, anime_id: int, count: int):
        with self.get_connection() as conn:
            conn.execute('UPDATE anime SET total_episodes = ? WHERE id = ?', (count, anime_id))
    
    def _remove_anime(self, anime_id: int):
        with self.get_connection() as conn:
            conn.execute('DELETE FROM anime WHERE id = ?', (anime_id,))
    
    def _remove_episode(self, episode_id: int):
        with self.get_connection() as conn:
            conn.execute('DELETE FROM episodes WHERE id = ?', (episode_id,))