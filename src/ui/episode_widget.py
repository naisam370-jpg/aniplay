from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class EpisodeWidget(QWidget):
    def __init__(self, title, frame_path):
        super().__init__()
        # Ensure it looks in src/ui/ for the ui file
        ui_file = Path(__file__).parent / "episode_widget.ui"
        layout = QVBoxLayout(self)

        # Thumbnail Label
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(200, 112)  # 16:9 Aspect Ratio
        self.thumb_label.setScaledContents(True)

        if thumb_path:
            self.thumb_label.setPixmap(QPixmap(thumb_path))
        else:
            self.thumb_label.setText("No Preview")
            self.thumb_label.setStyleSheet("background-color: #333;")

        # Title Label
        self.title_label = QLabel(title)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("font-weight: bold; color: white;")

        layout.addWidget(self.thumb_label)
        layout.addWidget(self.title_label)