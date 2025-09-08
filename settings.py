import json
import os

class SettingsManager:
    DEFAULTS = {
        "library_path": "library",
        "covers_path": "covers",
        "auto_refresh": False
    }

    def __init__(self, filename="settings.json"):
        self.filename = filename
        self.settings = self.DEFAULTS.copy()
        self.load()

        # ensure directories exist
        os.makedirs(self.settings["library_path"], exist_ok=True)
        os.makedirs(self.settings["covers_path"], exist_ok=True)

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    data = json.load(f)
                    self.settings.update(data)
            except Exception as e:
                print(f"[Settings] Failed to load {self.filename}: {e}")

    def save(self):
        try:
            with open(self.filename, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"[Settings] Failed to save {self.filename}: {e}")

    def get(self, key):
        return self.settings.get(key, self.DEFAULTS.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save()
