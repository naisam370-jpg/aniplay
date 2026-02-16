import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

# Path setup
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(ROOT_DIR / "src"))

from ui.main_window import MainWindow
from core.database import DatabaseManager  # Import the real DB manager


class AppLauncher:
    def __init__(self):
        # Initialize the REAL database
        self.db = DatabaseManager()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create the launcher with the real DB
    launcher = AppLauncher()

    window = MainWindow(launcher)
    window.show()

    print("App is running with Database connected")
    sys.exit(app.exec())