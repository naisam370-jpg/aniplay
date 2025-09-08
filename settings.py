# settings.py
import json
import os

SETTINGS_FILE = "settings.json"

# Default settings
DEFAULT_SETTINGS = {
    "theme": "light",          # light or dark
    "covers_enabled": True,    # fetch cover art automatically
    "precache_covers": False,  # pre-cache covers at startup
    "scroll_speed": 1,         # integer multiplier
    "library_path": "library", # path to anime library
    "covers_path": "covers"    # path to store covers
}

def load_settings():
    """Load settings from JSON file, fallback to defaults."""
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Merge with defaults in case new keys were added later
        merged = DEFAULT_SETTINGS.copy()
        merged.update(data)
        return merged
    except Exception:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings: dict):
    """Save settings to JSON file."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")

def reset_settings():
    """Reset settings to default values."""
    save_settings(DEFAULT_SETTINGS)
    return DEFAULT_SETTINGS.copy()
