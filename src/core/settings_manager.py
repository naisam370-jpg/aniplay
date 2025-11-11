import json
import os

class SettingsManager:
    def __init__(self, settings_path="settings.json"):
        self.settings_path = settings_path
        self.settings = {}
        self.load_settings()

    def load_settings(self):
        """Loads settings from the JSON file if it exists."""
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r') as f:
                    self.settings = json.load(f)
                print(f"Settings loaded from {self.settings_path}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading settings file: {e}. Using default settings.")
                self.settings = {}
        else:
            print("No settings file found. Using default settings.")

    def get(self, key, default=None):
        """
        Gets a value from the settings.

        Args:
            key (str): The key for the setting.
            default: The default value to return if the key is not found.

        Returns:
            The value of the setting, or the default value.
        """
        return self.settings.get(key, default)

    def set(self, key, value):
        """
        Sets a value in the settings and saves it to the file.

        Args:
            key (str): The key for the setting.
            value: The value to set.
        """
        self.settings[key] = value
        self.save_settings()

    def save_settings(self):
        """Saves the current settings to the JSON file."""
        try:
            with open(self.settings_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
            print(f"Settings saved to {self.settings_path}")
        except IOError as e:
            print(f"Error saving settings file: {e}")

if __name__ == '__main__':
    # Example Usage
    sm = SettingsManager("test_settings.json")

    # Set some settings
    sm.set("library_path", "/path/to/my/anime")
    sm.set("auto_scan_on_startup", True)
    sm.set("volume", 80)

    # Get some settings
    print(f"Library Path: {sm.get('library_path')}")
    print(f"Volume: {sm.get('volume')}")
    print(f"Non-existent setting: {sm.get('non_existent', 'default_value')}")

    # Create a new manager instance to test loading
    sm2 = SettingsManager("test_settings.json")
    print(f"Library Path (from new instance): {sm2.get('library_path')}")

    # Clean up test file
    if os.path.exists("test_settings.json"):
        os.remove("test_settings.json")
