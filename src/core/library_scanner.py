import os
import re
from collections import defaultdict
from src.core.filename_parser import parse_filename
from src.core.database_manager import DatabaseManager

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"}

def _get_season_from_path(relative_path):
    """
    Attempts to extract a season number from a given relative path.
    Looks for patterns like 'Season X', 'SX', 'SXX'.
    """
    path_parts = relative_path.split(os.sep)
    for part in path_parts:
        # Pattern for "Season X" or "SXX"
        match = re.search(r"(?:season|s)(\d+)", part, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None # Return None if no season found in path, so filename can take precedence or default to 1

def scan_library(path, db_manager: DatabaseManager):
    """
    Scans a given directory path for video files, parses their information,
    and stores them in the database.
    """
    scanned_video_data = []
    if not os.path.isdir(path):
        print(f"Error: Path '{path}' is not a valid directory.")
        return scanned_video_data

    # Iterate through first-level directories in the given path
    for entry in os.listdir(path):
        full_entry_path = os.path.join(path, entry)
        if os.path.isdir(full_entry_path):
            # This is a main anime folder
            anime_title = entry # The folder name is the anime title

            # Now, walk through this anime's folder to find all video files
            for root, _, files in os.walk(full_entry_path):
                # Determine season from the current root path relative to the anime's main folder
                current_relative_root = os.path.relpath(root, full_entry_path)
                path_season = _get_season_from_path(current_relative_root)

                for file in files:
                    if os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS:
                        full_path = os.path.join(root, file)
                        
                        parsed_info = parse_filename(file)
                        
                        # Determine final season: prioritize path_season, then filename season, then default to 1
                        final_season = 1
                        if path_season is not None:
                            final_season = path_season
                        elif parsed_info.get("season") is not None:
                            final_season = parsed_info.get("season")
                        
                        episode = parsed_info.get("episode")

                        db_manager.add_episode(full_path, anime_title, episode, final_season)
                        scanned_video_data.append({
                            "file_path": full_path,
                            "title": anime_title,
                            "episode": episode,
                            "season": final_season
                        })
    
    return scanned_video_data

def load_library_from_db(db_manager: DatabaseManager):
    """Loads all anime episodes from the database."""
    return db_manager.get_all_episodes()

def group_episodes_by_anime(episodes_list):
    """
    Groups a flat list of episode dictionaries by anime title and then by season.
    """
    anime_groups = defaultdict(lambda: defaultdict(list))
    for episode in episodes_list:
        anime_groups[episode['title']][episode['season']].append(episode)

    grouped_list = []
    for title, seasons in anime_groups.items():
        series_seasons = []
        for season_num in sorted(seasons.keys()):
            series_seasons.append({
                "season_num": season_num,
                "episodes": sorted(seasons[season_num], key=lambda x: x['episode'] if x['episode'] is not None else 0)
            })
        grouped_list.append({
            "title": title,
            "seasons": series_seasons
        })
    
    # Sort by title
    return sorted(grouped_list, key=lambda x: x['title'])

if __name__ == '__main__':
    # Example usage:
    test_path = os.path.expanduser('~/Videos') 
    test_db_manager = DatabaseManager("test_aniplay.db")
    
    print(f"Scanning for videos in: {test_path}")
    scan_library(test_path, test_db_manager)

    print("\nLoading library from DB:")
    db_episodes = load_library_from_db(test_db_manager)
    
    print("\nGrouping episodes by anime:")
    grouped_anime = group_episodes_by_anime(db_episodes)
    for anime in grouped_anime:
        print(f"Anime: {anime['title']}")
        for season_data in anime.get('seasons', []):
            print(f"  Season {season_data['season_num']}: {len(season_data['episodes'])} episodes")
            for ep in season_data['episodes']:
                print(f"    - S{ep['season']}E{ep['episode']} - {os.path.basename(ep['file_path'])}")

    test_db_manager.close()
    if os.path.exists("test_aniplay.db"):
        os.remove("test_aniplay.db")
