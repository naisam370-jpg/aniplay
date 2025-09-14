import os

def precache_covers(library_path, covers_path):
    """
    For now, just ensure cover placeholders exist for each series.
    """
    os.makedirs(covers_path, exist_ok=True)

    series_folders = [
        d for d in sorted(os.listdir(library_path))
        if os.path.isdir(os.path.join(library_path, d))
    ]

    for series in series_folders:
        cover_file = os.path.join(covers_path, f"{series}.jpg")
        if not os.path.exists(cover_file):
            # Just leave it missing, GUI will use placeholder
            continue


def ensure_episode_thumbnail(series_name, episode_path, covers_path):
    """
    For now, just reuse the series cover as the episode thumbnail.
    """
    cover_file = os.path.join(covers_path, f"{series_name}.jpg")
    if os.path.exists(cover_file):
        return cover_file
    return None
