import re
from pathlib import Path


class EpisodeParser:
    def __init__(self):
        # Pattern 1: S01E01 or s1e1
        self.se_pattern = re.compile(r'[Ss](\d+)[Ee](\d+)', re.I)
        # Pattern 2: "Episode 01" or "Ep 01"
        self.ep_only_pattern = re.compile(r'(?:episode|ep|e)\s*(\d+)', re.I)
        # Pattern 3: Season folder names like "Season 02"
        self.season_folder_pattern = re.compile(r'season\s*(\d+)', re.I)

    def parse_path(self, file_path):
        path_obj = Path(file_path)
        filename = path_obj.name
        parent_name = path_obj.parent.name

        season = 1
        episode = 0

        # Step 1: Check if the file is inside a "Season XX" folder
        folder_match = self.season_folder_pattern.search(parent_name)
        if folder_match:
            season = int(folder_match.group(1))

        # Step 2: Try to find S01E01 in the filename (overwrites folder season if found)
        se_match = self.se_pattern.search(filename)
        if se_match:
            season = int(se_match.group(1))
            episode = int(se_match.group(2))
        else:
            # Step 3: If no S01E01, just look for the episode number
            ep_match = self.ep_only_pattern.search(filename)
            if ep_match:
                episode = int(ep_match.group(1))

        return season, episode