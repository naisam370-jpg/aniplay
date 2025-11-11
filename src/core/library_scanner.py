import os
import re
from collections import defaultdict
from src.core.filename_parser import parse_filename
from src.core.database_manager import DatabaseManager

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"}

def _clean_title_from_folder_name(folder_name):
    """
    Applies cleaning logic similar to filename_parser to a folder name
    to derive a clean anime title for metadata fetching.
    """
    cleaned_name = folder_name.replace("_", " ").replace(".", " ").strip()
    cleaned_name = re.sub(r"\[.*?\]", "", cleaned_name) # Remove bracketed tags
    cleaned_name = re.sub(r"\(.*?\)", "", cleaned_name) # Remove parenthesized tags
    cleaned_name = re.sub(r"\b(?:S\d+|Season\s*\d+)\b", "", cleaned_name, flags=re.IGNORECASE) # Remove season tags
    cleaned_name = re.sub(r"\b\d{4}\b", "", cleaned_name) # Remove years
    cleaned_name = re.sub(r"\s+", " ", cleaned_name).strip() # Normalize spaces
    
    # Capitalize first letter of each word for title
    return ' '.join(word.capitalize() for word in cleaned_name.split()) if cleaned_name else folder_name

def scan_library(path, db_manager: DatabaseManager):
    """
    Scans a given directory path for video files, parses their information,
    and stores them in the database, organizing them hierarchically.
    """
    scanned_video_data = []
    if not os.path.isdir(path):
        print(f"Error: Path '{path}' is not a valid directory.")
        return scanned_video_data

    # Iterate through first-level directories in the given path (main anime folders)
    for entry in os.listdir(path):
        full_entry_path = os.path.join(path, entry)
        if os.path.isdir(full_entry_path):
            folder_name = entry # The first-level folder name
            cleaned_main_anime_title = _clean_title_from_folder_name(folder_name)

            # Collect all video files and subdirectories within this main anime folder
            all_files_in_main_anime = []
            all_subdirs_in_main_anime = []

            for root, dirs, files in os.walk(full_entry_path):
                # Get relative path from the main anime folder
                relative_root = os.path.relpath(root, full_entry_path)
                
                for file in files:
                    if os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS:
                        full_path = os.path.join(root, file)
                        all_files_in_main_anime.append((full_path, relative_root, file))
                
                # Collect immediate subdirectories for processing as sub-series
                if root == full_entry_path: # Only consider direct subdirectories
                    for d in dirs:
                        all_subdirs_in_main_anime.append(d)

            # Determine if there are sub-series (folders containing video files)
            # or if all videos are directly under the main folder
            has_sub_series = False
            for subdir_name in all_subdirs_in_main_anime:
                subdir_path = os.path.join(full_entry_path, subdir_name)
                # Check if this subdirectory actually contains video files
                for r, _, f in os.walk(subdir_path):
                    if any(os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS for file in f):
                        has_sub_series = True
                        break
                if has_sub_series:
                    break

            if has_sub_series:
                # Process sub-series folders
                for subdir_name in all_subdirs_in_main_anime:
                    subdir_path = os.path.join(full_entry_path, subdir_name)
                    # Only process if it's a directory and contains video files
                    if os.path.isdir(subdir_path):
                        # Walk through this subdirectory to find video files
                        for root, _, files in os.walk(subdir_path):
                            for file in files:
                                if os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS:
                                    full_path = os.path.join(root, file)
                                    parsed_info = parse_filename(file)
                                    
                                    episode = parsed_info.get("episode")
                                    # Season is 1 for sub-series, sub_series_title is the folder name
                                    season = 1 
                                    sub_series_title = subdir_name

                                    db_manager.add_episode(full_path, cleaned_main_anime_title, episode, season, sub_series_title)
                                    scanned_video_data.append({
                                        "file_path": full_path,
                                        "title": cleaned_main_anime_title,
                                        "episode": episode,
                                        "season": season,
                                        "sub_series_title": sub_series_title
                                    })
            
                # Process any files directly in the main folder that are not part of a sub-series
                # This is a bit tricky, as os.walk will also find files in subdirs.
                # We need to find files whose relative_root is just '.'
                for full_path, relative_root, file in all_files_in_main_anime:
                    if relative_root == '.': # File is directly in the main anime folder
                        parsed_info = parse_filename(file)
                        episode = parsed_info.get("episode")
                        season = 0 # Season 0 for main series episodes
                        sub_series_title = None

                        db_manager.add_episode(full_path, cleaned_main_anime_title, episode, season, sub_series_title)
                        scanned_video_data.append({
                            "file_path": full_path,
                            "title": cleaned_main_anime_title,
                            "episode": episode,
                            "season": season,
                            "sub_series_title": sub_series_title
                        })

            else:
                # No subdirectories with video files, so all video files belong to the main anime title
                for full_path, relative_root, file in all_files_in_main_anime:
                    parsed_info = parse_filename(file)
                    episode = parsed_info.get("episode")
                    season = 0 # Season 0 for main series episodes
                    sub_series_title = None

                    db_manager.add_episode(full_path, cleaned_main_anime_title, episode, season, sub_series_title)
                    scanned_video_data.append({
                        "file_path": full_path,
                        "title": cleaned_main_anime_title,
                        "episode": episode,
                        "season": season,
                        "sub_series_title": sub_series_title
                    })
    
    return scanned_video_data

def load_library_from_db(db_manager: DatabaseManager):
    """Loads all anime episodes from the database."""
    return db_manager.get_all_episodes()

def group_episodes_by_anime(episodes_list):
    """
    Groups a flat list of episode dictionaries into a hierarchical structure:
    Main Anime -> Sub-series (Seasons/Movies) -> Episodes.
    """
    grouped_anime_data = defaultdict(lambda: {
        "title": None,
        "sub_series": defaultdict(lambda: {"title": None, "episodes": []}),
        "episodes": [] # For episodes directly under the main anime folder
    })

    for episode in episodes_list:
        main_anime_title = episode['title']
        grouped_anime_data[main_anime_title]["title"] = main_anime_title

        if episode['sub_series_title']:
            sub_series_title = episode['sub_series_title']
            grouped_anime_data[main_anime_title]["sub_series"][sub_series_title]["title"] = sub_series_title
            grouped_anime_data[main_anime_title]["sub_series"][sub_series_title]["episodes"].append(episode)
        else:
            grouped_anime_data[main_anime_title]["episodes"].append(episode)

    final_grouped_list = []
    for main_title, data in grouped_anime_data.items():
        main_anime_entry = {
            "title": main_title,
            "sub_series": [],
            "episodes": sorted(data["episodes"], key=lambda x: x['episode'] if x['episode'] is not None else 0)
        }

        # Convert sub_series defaultdict to a sorted list
        for sub_series_title, sub_series_data in sorted(data["sub_series"].items()):
            main_anime_entry["sub_series"].append({
                "title": sub_series_title,
                "episodes": sorted(sub_series_data["episodes"], key=lambda x: x['episode'] if x['episode'] is not None else 0)
            })
        
        final_grouped_list.append(main_anime_entry)
    
    # Sort main anime entries by title
    return sorted(final_grouped_list, key=lambda x: x['title'])

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
        if anime['episodes']:
            print("  Direct Episodes:")
            for ep in anime['episodes']:
                print(f"    - E{ep['episode']} - {os.path.basename(ep['file_path'])}")
        for sub_series in anime['sub_series']:
            print(f"  Sub-series: {sub_series['title']}")
            for ep in sub_series['episodes']:
                print(f"    - E{ep['episode']} - {os.path.basename(ep['file_path'])}")

    test_db_manager.close()
    if os.path.exists("test_aniplay.db"):
        os.remove("test_aniplay.db")
