import re
import os

def parse_filename(filename):
    """
    Attempts to parse an anime title and episode number from a filename.

    Args:
        filename (str): The base filename (e.g., "My Anime - 01 - Episode Title.mkv").

    Returns:
        dict: A dictionary containing 'title' and 'episode' (or None if not found).
    """
    result = {"title": None, "episode": None}

    # Remove extension for easier parsing
    base_name = os.path.splitext(filename)[0]

    # Pattern 1: "Anime Title - 01 - Episode Name" or "Anime Title - 01"
    match = re.search(r"^(.*?)[-_\s\.](\d+)(?:[-_\s\.]|$)(.*)", base_name)
    if match:
        title_part = match.group(1).strip()
        episode_part = match.group(2).strip()
        
        # Clean up title part (remove common release group tags, year, etc.)
        title_part = re.sub(r"\[.*?\]", "", title_part) # Remove bracketed tags
        title_part = re.sub(r"\(.*?\)", "", title_part) # Remove parenthesized tags
        title_part = re.sub(r"\b(?:S\d+|Season\s*\d+)\b", "", title_part, flags=re.IGNORECASE) # Remove season tags
        title_part = re.sub(r"\b\d{4}\b", "", title_part) # Remove years
        title_part = title_part.replace("_", " ").replace(".", " ").strip()
        
        # Capitalize first letter of each word for title
        result["title"] = ' '.join(word.capitalize() for word in title_part.split()) if title_part else None
        result["episode"] = int(episode_part) if episode_part.isdigit() else None
        return result

    # Pattern 2: "Anime Title S01E01" or "Anime Title E01"
    match = re.search(r"^(.*?)[-_\s\.]S?\d*E(\d+)(?:[-_\s\.]|$)(.*)", base_name, re.IGNORECASE)
    if match:
        title_part = match.group(1).strip()
        episode_part = match.group(2).strip()

        title_part = re.sub(r"\[.*?\]", "", title_part)
        title_part = re.sub(r"\(.*?\)", "", title_part)
        title_part = re.sub(r"\b(?:S\d+|Season\s*\d+)\b", "", title_part, flags=re.IGNORECASE)
        title_part = re.sub(r"\b\d{4}\b", "", title_part)
        title_part = title_part.replace("_", " ").replace(".", " ").strip()

        result["title"] = ' '.join(word.capitalize() for word in title_part.split()) if title_part else None
        result["episode"] = int(episode_part) if episode_part.isdigit() else None
        return result

    # Fallback: If no pattern matches, use the cleaned filename as title
    cleaned_name = base_name.replace("_", " ").replace(".", " ").strip()
    cleaned_name = re.sub(r"\[.*?\]", "", cleaned_name)
    cleaned_name = re.sub(r"\(.*?\)", "", cleaned_name)
    cleaned_name = re.sub(r"\b(?:S\d+|Season\s*\d+)\b", "", cleaned_name, flags=re.IGNORECASE)
    cleaned_name = re.sub(r"\b\d{4}\b", "", cleaned_name)
    result["title"] = ' '.join(word.capitalize() for word in cleaned_name.split()) if cleaned_name else filename
    result["episode"] = None # No episode found

    return result

if __name__ == '__main__':
    test_filenames = [
        "[SubsPlease] My Anime - 01 (1080p) [ABCDEF12].mkv",
        "Awesome Show - 12.mp4",
        "Another.Anime.S01E05.Title.mkv",
        "Anime_Movie_2023.avi",
        "Just.A.Title.mp4",
        "Series Name - Episode 03.mov",
        "Series.Name.E04.flv",
        "One Piece - 1000 - Luffy's New Gear.mkv",
        "Spy x Family - 25.mkv",
        "Boku no Hero Academia S6 - 25.mkv"
    ]

    for fname in test_filenames:
        parsed = parse_filename(fname)
        print(f"Original: '{fname}' -> Parsed: {parsed}")
