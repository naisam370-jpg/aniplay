import json
import os

SETTINGS_FILE = os.path.expanduser("settings.json")

DEFAULT_SETTINGS = {
    "theme": "dark",          # dark / light
    "player": "mpv",          # video player
    "covers_auto_fetch": True, # auto fetch covers
    "cover_size": "large",  # small / medium / large
    "sort_mode": "recent",    # name / recent / unwatched
    "filter_mode": "all",     # all / unwatched / completed
}


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

def get_setting(key, default=None):
    settings = load_settings()
    return settings.get(key, default)

def set_setting(key, value):
    settings = load_settings()
    settings[key] = value
    save_settings(settings)