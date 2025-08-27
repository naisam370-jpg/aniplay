# gui.py
import sys
import ctypes
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog

# Load backend
lib = ctypes.cdll.LoadLibrary("./build/libaniplay.so")
lib.aniplay_init.restype = ctypes.c_bool
lib.aniplay_load.argtypes = [ctypes.c_char_p]
lib.aniplay_load.restype = ctypes.c_bool

class AniPlayUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AniPlay Prototype")

        layout = QVBoxLayout()

        self.btn_open = QPushButton("Open Video")
        self.btn_open.clicked.connect(self.open_file)
        layout.addWidget(self.btn_open)

        self.setLayout(layout)

        # Initialize backend
        if not lib.aniplay_init():
            print("Failed to init backend")
            sys.exit(1)

    def open_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select video")
        if file:
            print("Playing:", file)
            lib.aniplay_load(file.encode("utf-8"))

    def closeEvent(self, event):
        lib.aniplay_shutdown()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AniPlayUI()
    win.resize(300, 100)
    win.show()
    sys.exit(app.exec())
