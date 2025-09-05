"""
config.py

Simple JSON config manager for AniPlay.

Stores config at: ~/.config/aniplay/config.json

Usage:
    from config import load_config, get, set, save_config
    cfg = load_config()
    print(get("library_path"))
    set("ui.theme", "light")
    save_config()
"""

import json
from pathlib import Path
import os
import shutil
import tempfile

CONFIG_DIR = Path.home() / ".config" / "aniplay"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Default configuration values
DEFAULT_CONFIG = {
    "version": "0.1.0",
    "library_path": str(Path.cwd() / "library"),
    "covers_path": str(Path.cwd() / "covers"),
    "auto_fetch_covers": True,
    "player": {
        "backend": "mpv",
        "executable": "mpv",
        "args": ["--force-window=yes"]
    },
    "subtitles": {
        "default_language": "",
        "font_size": 24
    },
    "ui": {
        "theme": "dark",
        "thumbnail_size": 320,
        "poster_size": 220
    },
    "resume": {
        "enabled": False
    },
    "general": {
        "clear_thumbnail_cache_on_exit": False
    }
}

# in-memory cache of loaded config
_config = None


# ----------------------
# Helpers
# ----------------------
def _ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _atomic_write(path: Path, data: str):
    """
    Write `data` to `path` atomically.
    """
    fd, tmp_path = tempfile.mkstemp(prefix="cfg-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp_path, str(path))
    except Exception:
        # cleanup
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        raise


def _deep_get(dct: dict, key_path: str, default=None):
    if not key_path:
        return dct
    cur = dct
    for part in key_path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur


def _deep_set(dct: dict, key_path: str, value):
    parts = key_path.split(".")
    cur = dct
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


# ----------------------
# Public API
# ----------------------
def load_config() -> dict:
    """
    Load configuration from CONFIG_FILE (create defaults if missing).
    Returns the config dict (also cached in memory).
    """
    global _config
    if _config is not None:
        return _config

    _ensure_config_dir()

    # if config file missing, create with defaults
    if not CONFIG_FILE.exists():
        _config = DEFAULT_CONFIG.copy()
        save_config(_config)
        # Ensure library/covers dirs exist as per defaults
        ensure_paths_exist(_config)
        return _config

    # read file
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Merge missing keys from DEFAULT_CONFIG (non-destructive)
        merged = _merge_defaults(DEFAULT_CONFIG, data)
        _config = merged
    except Exception as e:
        # Backup corrupted config and rewrite defaults
        backup = CONFIG_DIR / f"config.corrupt.backup.json"
        shutil.copy2(CONFIG_FILE, backup)
        _config = DEFAULT_CONFIG.copy()
        save_config(_config)
        print(f"[config] Corrupt config detected. Backed up to {backup}. Recreated defaults.")
    # ensure paths exist
    ensure_paths_exist(_config)
    return _config


def save_config(cfg: dict = None):
    """
    Save config to disk. If cfg is None, saves the in-memory config.
    """
    global _config
    if cfg is None:
        if _config is None:
            raise RuntimeError("No config loaded")
        cfg = _config

    _ensure_config_dir()
    text = json.dumps(cfg, indent=2, ensure_ascii=False)
    _atomic_write(CONFIG_FILE, text)
    _config = cfg.copy()


def get(key_path: str = "", default=None):
    """
    Get a config value. Use dot notation for nested keys, e.g. "ui.theme".
    If key_path is empty, returns full config dict.
    """
    cfg = load_config()
    if not key_path:
        return cfg
    return _deep_get(cfg, key_path, default)


def set(key_path: str, value):
    """
    Set a config value (dot notation supported) and update in-memory config.
    Does not auto-save; call save_config() to persist.
    """
    cfg = load_config()
    _deep_set(cfg, key_path, value)
    # update in-memory
    global _config
    _config = cfg
    return cfg


def reset_defaults():
    """
    Overwrite config with DEFAULT_CONFIG.
    """
    global _config
    _config = DEFAULT_CONFIG.copy()
    save_config(_config)
    ensure_paths_exist(_config)


def ensure_paths_exist(cfg: dict):
    """
    Ensure library and covers directories referenced in config exist on disk.
    """
    try:
        lib = Path(cfg.get("library_path") or DEFAULT_CONFIG["library_path"])
        covers = Path(cfg.get("covers_path") or DEFAULT_CONFIG["covers_path"])
        lib.mkdir(parents=True, exist_ok=True)
        covers.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[config] Failed to ensure library/covers paths: {e}")


def _merge_defaults(base: dict, user: dict) -> dict:
    """
    Merge `user` on top of `base` recursively, but keep base keys that are missing.
    Returns a new dict.
    """
    out = {}
    for k, v in base.items():
        if k in user:
            if isinstance(v, dict) and isinstance(user[k], dict):
                out[k] = _merge_defaults(v, user[k])
            else:
                out[k] = user[k]
        else:
            out[k] = v
    # include any additional keys present in user but not in base
    for k, v in user.items():
        if k not in out:
            out[k] = v
    return out


# ----------------------
# CLI debug helper
# ----------------------
if __name__ == "__main__":
    cfg = load_config()
    print("Loaded config from:", CONFIG_FILE)
    print(json.dumps(cfg, indent=2, ensure_ascii=False))
