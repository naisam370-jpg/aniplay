import os
import sys
from pathlib import Path

# 1. SETUP PATHS
# ROOT_DIR is .../aniplay
ROOT_DIR = Path(__file__).parent.absolute()
# SRC_DIR is .../aniplay/src
SRC_DIR = ROOT_DIR / "src"

# Add 'src' to the Python path so it can see 'core'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# 2. WINDOWS DLL FIX
os.environ["PATH"] = str(ROOT_DIR) + os.pathsep + os.environ["PATH"]
if hasattr(os, 'add_dll_directory'):
    try:
        os.add_dll_directory(str(ROOT_DIR))
    except Exception:
        pass

# Debug prints to confirm
print(f"Checking for 'core' in: {SRC_DIR}")
print(f"Does 'src/core' exist? {(SRC_DIR / 'core').exists()}")

# 3. IMPORTS
try:
    from core.database import DatabaseManager
    from core.scanner import ScannerWorker

    print("✅ Success: Modules imported correctly from src/core!")
except ImportError as e:
    print(f"❌ Still failing. Error: {e}")
    sys.exit(1)


def start_test_scan(target_path):
    print("\n--- Aniplay First Run: Backend Test ---")
    db = DatabaseManager()
    print(f"✅ Database initialized at: {db.db_path}")

    scanner = ScannerWorker(target_path, db)

    scanner.signals.found_anime.connect(lambda name: print(f"📂 Found Anime: {name}"))
    scanner.signals.progress.connect(lambda msg: print(f"  > {msg}"))
    scanner.signals.finished.connect(lambda count: print(f"\n✨ SUCCESS! Indexed {count} episodes."))

    print(f"🚀 Starting scan of: {target_path}...")
    scanner.run()


if __name__ == "__main__":
    # Ensure this path is correct for your machine
    MY_ANIME_PATH = r"C:\Users\Naisam\Desktop\Anime\Love, Chuunibyou and other Delusions"

    if os.path.exists(MY_ANIME_PATH):
        start_test_scan(MY_ANIME_PATH)
    else:
        print(f"❌ Error: The path '{MY_ANIME_PATH}' does not exist.")