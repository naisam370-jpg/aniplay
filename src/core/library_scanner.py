import os
from collections import defaultdict
from src.core.filename_parser import parse_filename
from src.core.database_manager import DatabaseManager

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"}

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
                for file in files:
                    if os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS:
                        full_path = os.path.join(root, file)
                        parsed_info = parse_filename(file)
                        
                        # Use the anime_title derived from the folder name,
                        # but still try to get episode number from the filename
                        episode = parsed_info.get("episode")

                        db_manager.add_episode(full_path, anime_title, episode)
                        scanned_video_data.append({
                            "file_path": full_path,
                            "title": anime_title,
                            "episode": episode
                        })
    
    return scanned_video_data

def load_library_from_db(db_manager: DatabaseManager):
    """Loads all anime episodes from the database."""
    return db_manager.get_all_episodes()

def group_episodes_by_anime(episodes_list):
    """
    Groups a flat list of episode dictionaries by anime title.
    """
    anime_groups = defaultdict(list)
    for episode in episodes_list:
        anime_groups[episode['title']].append(episode)

    # Convert the defaultdict to a list of dictionaries
    grouped_list = []
    for title, episodes in anime_groups.items():
        grouped_list.append({
            "title": title,
            "episodes": episodes
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
        print(f"Anime: {anime['title']}, Episodes: {len(anime['episodes'])}")

    test_db_manager.close()
    if os.path.exists("test_aniplay.db"):
        os.remove("test_aniplay.db")
