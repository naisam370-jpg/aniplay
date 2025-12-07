import os
import re
from collections import defaultdict
from src.core.filename_parser import parse_filename
from src.core.database_manager import DatabaseManager

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"}

def _clean_title_from_folder_name(folder_name):
    """
    Cleans a folder name to derive a clean anime title.
    """
    cleaned_name = folder_name.replace("_", " ").replace(".", " ").strip()
    cleaned_name = re.sub(r"\[.*?\]", "", cleaned_name)
    cleaned_name = re.sub(r"\(.*?\)", "", cleaned_name)
    cleaned_name = re.sub(r"\b(?:S\d+|Season\s*\d+)\b", "", cleaned_name, flags=re.IGNORECASE)
    cleaned_name = re.sub(r"\b\d{4}\b", "", cleaned_name)
    cleaned_name = re.sub(r"\s+", " ", cleaned_name).strip()
    return ' '.join(word.capitalize() for word in cleaned_name.split()) if cleaned_name else folder_name

def scan_library(path, db_manager: DatabaseManager):
    """
    Scans a directory for video files, parses their information,
    and stores them in the database.
    """
    scanned_video_data = []
    if not os.path.isdir(path):
        print(f"Error: Path '{path}' is not a valid directory.")
        return scanned_video_data

    for entry in os.listdir(path):
        full_entry_path = os.path.join(path, entry)
        if os.path.isdir(full_entry_path):
            folder_name = entry
            cleaned_main_anime_title = _clean_title_from_folder_name(folder_name)
            series_id = db_manager.add_or_get_series(cleaned_main_anime_title)

            all_files_in_main_anime = []
            all_subdirs_in_main_anime = []

            for root, dirs, files in os.walk(full_entry_path):
                relative_root = os.path.relpath(root, full_entry_path)
                for file in files:
                    if os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS:
                        all_files_in_main_anime.append((os.path.join(root, file), relative_root, file))
                if root == full_entry_path:
                    for d in dirs:
                        all_subdirs_in_main_anime.append(d)

            has_sub_series = False
            for subdir_name in all_subdirs_in_main_anime:
                subdir_path = os.path.join(full_entry_path, subdir_name)
                # Check if this subdirectory actually contains video files
                if os.path.isdir(subdir_path): # Ensure it's actually a directory
                    for r, _, files in os.walk(subdir_path):
                        if any(os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS for file in files):
                            has_sub_series = True
                            break
                if has_sub_series:
                    break
            
            if has_sub_series:
                for subdir_name in all_subdirs_in_main_anime:
                    for root, _, files in os.walk(os.path.join(full_entry_path, subdir_name)):
                        for file in files:
                            if os.path.splitext(file)[1].lower() in VIDEO_EXTENSIONS:
                                full_path = os.path.join(root, file)
                                parsed_info = parse_filename(file)
                                episode = parsed_info.get("episode")
                                db_manager.add_episode(series_id, full_path, episode, season=1, sub_series_title=subdir_name)
                                scanned_video_data.append({"file_path": full_path, "title": cleaned_main_anime_title})
            
            # Process files directly in the main folder
            for full_path, relative_root, file in all_files_in_main_anime:
                if relative_root == '.':
                    parsed_info = parse_filename(file)
                    episode = parsed_info.get("episode")
                    db_manager.add_episode(series_id, full_path, episode, season=0, sub_series_title=None)
                    scanned_video_data.append({"file_path": full_path, "title": cleaned_main_anime_title})
    
    return scanned_video_data

def load_library_from_db(db_manager: DatabaseManager):
    """Loads all anime episodes from the database."""
    return db_manager.get_all_episodes_with_series_info()

def group_episodes_by_anime(episodes_list):
    """
    Groups a flat list of episode dictionaries into a hierarchical structure.
    """
    grouped_anime_data = defaultdict(lambda: {
        "title": None,
        "sub_series": defaultdict(lambda: {"title": None, "episodes": []}),
        "episodes": []
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

        for sub_series_title, sub_series_data in sorted(data["sub_series"].items()):
            main_anime_entry["sub_series"].append({
                "title": sub_series_title,
                "episodes": sorted(sub_series_data["episodes"], key=lambda x: x['episode'] if x['episode'] is not None else 0)
            })
        
        final_grouped_list.append(main_anime_entry)
    
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
    # ... (rest of the example is the same)
