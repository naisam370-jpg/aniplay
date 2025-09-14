import json
import os

HISTORY_FILE = "history.json"

def load_history():
    if not os.path.exists(HISTORY_FILE):
        save_history({})
        return {}
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def update_history(series_name, episode_file, position, completed=False):
    history = load_history()
    history[series_name] = {
        "last_watched": episode_file,
        "position": position,
        "completed": completed
    }
    save_history(history)

def get_resume_info(series_name):
    history = load_history()
    return history.get(series_name)
