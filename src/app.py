import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow

# Setup paths for our 'src' folder
ROOT_DIR = Path(__file__).parent.absolute()
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from .ui.ui_mainwindow import Ui_MainWindow
except ImportError:
    print("Error: Could not find ui_mainwindow.py. Did you run the pyside6-uic command?")
    sys.exit(1)


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Test: Switch to the Library page on launch
        # Assuming Library is the second page (index 1)
        if hasattr(self.ui, 'stacked_widget'):
            self.ui.stacked_widget.setCurrentIndex(1)
            print("UI Loaded and switched to Library page.")
        else:
            print("Warning: 'stacked_widget' object name not found. Check your Designer naming.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())