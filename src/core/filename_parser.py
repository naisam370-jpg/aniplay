import re
import os

def parse_filename(filename):
    """
    Attempts to parse an anime title, episode number, and season number from a filename.

    Args:
        filename (str): The base filename (e.g., "My Anime - S01E01 - Episode Title.mkv").

    Returns:
        dict: A dictionary containing 'title', 'episode', and 'season' (or None/default if not found).
    """
    result = {"title": None, "episode": None, "season": 1} # Default season to 1

    # Remove extension for easier parsing
    base_name = os.path.splitext(filename)[0]

    # Try to extract season and episode first
    # Pattern for SXXEXX (e.g., S01E05) or EXX (e.g., E05)
    season_episode_match = re.search(r"(?:S(\d+))?E(\d+)", base_name, re.IGNORECASE)
    if season_episode_match:
        season_part = season_episode_match.group(1)
        episode_part = season_episode_match.group(2)
        if season_part:
            result["season"] = int(season_part)
        result["episode"] = int(episode_part)
        
        # Remove the matched season/episode part from base_name for title extraction
        base_name = re.sub(r"(?:S\d+)?E\d+", "", base_name, flags=re.IGNORECASE).strip()

    # Pattern for "Anime Title - 01 - Episode Name" or "Anime Title - 01"
    # This pattern should now primarily focus on episode if SXXEXX wasn't found
    if result["episode"] is None: # Only try this if episode wasn't found by SXXEXX pattern
        match = re.search(r"^(.*?)[-_\s\.](\d+)(?:[-_\s\.]|$)(.*)", base_name)
        if match:
            # If a season was already found, we don't want to re-extract episode from here
            # This part is tricky, let's simplify: if SXXEXX was found, we trust it.
            # If not, we try to get episode from this pattern.
            episode_part = match.group(2).strip()
            result["episode"] = int(episode_part) if episode_part.isdigit() else None
            base_name = match.group(1).strip() # Use the title part before the episode number

    # Clean up title part (remove common release group tags, year, etc.)
    cleaned_name = base_name
    cleaned_name = re.sub(r"\[.*?\]", "", cleaned_name) # Remove bracketed tags
    cleaned_name = re.sub(r"\(.*?\)", "", cleaned_name) # Remove parenthesized tags
    cleaned_name = re.sub(r"\b(?:S\d+|Season\s*\d+)\b", "", cleaned_name, flags=re.IGNORECASE) # Remove season tags
    cleaned_name = re.sub(r"\b\d{4}\b", "", cleaned_name) # Remove years
    cleaned_name = cleaned_name.replace("_", " ").replace(".", " ").strip()
    
    # Capitalize first letter of each word for title
    result["title"] = ' '.join(word.capitalize() for word in cleaned_name.split()) if cleaned_name else None
    if result["title"] is None:
        # Fallback if no title could be parsed, use a cleaned version of the original filename
        fallback_title = os.path.splitext(filename)[0]
        fallback_title = re.sub(r"\[.*?\]|\(.*?\)", "", fallback_title)
        fallback_title = re.sub(r"\b(?:S\d+|Season\s*\d+|E\d+)\b", "", fallback_title, flags=re.IGNORECASE)
        fallback_title = re.sub(r"\b\d{4}\b", "", fallback_title)
        fallback_title = fallback_title.replace("_", " ").replace(".", " ").strip()
        result["title"] = ' '.join(word.capitalize() for word in fallback_title.split()) if fallback_title else filename


    return result

if __name__ == '__main__':
    test_filenames = [
        "[SubsPlease] My Anime - 01 (1080p) [ABCDEF12].mkv", # Should get episode 1
        "Awesome Show - 12.mp4", # Should get episode 12
        "Another.Anime.S01E05.Title.mkv", # Should get season 1, episode 5
        "Anime_Movie_2023.avi", # Should get title, no episode/season
        "Just.A.Title.mp4", # Should get title, no episode/season
        "Series Name - Episode 03.mov", # Should get episode 3
        "Series.Name.E04.flv", # Should get episode 4
        "One Piece - 1000 - Luffy's New Gear.mkv", # Should get episode 1000
        "Spy x Family - 25.mkv", # Should get episode 25
        "Boku no Hero Academia S6 - 25.mkv", # Should get season 6, episode 25
        "Anime Title Season 2 Episode 10.mp4", # Should get season 2, episode 10
        "Anime.Title.S03.E01.mkv", # Should get season 3, episode 1
        "Movie Title.mp4" # Should get title, no episode/season
    ]

    for fname in test_filenames:
        parsed = parse_filename(fname)
        print(f"Original: '{fname}' -> Parsed: {parsed}")
