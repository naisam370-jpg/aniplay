from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap


class EpisodeItem(QWidget):
    clicked = Signal(str)  # Signal to send the file path when clicked

    def __init__(self, title, ep_number, thumb_path, file_path):
        super().__init__()
        layout = QHBoxLayout(self)

        # 1. Thumbnail
        self.thumb = QLabel()
        self.thumb.setFixedSize(160, 90)  # 16:9 ratio
        pixmap = QPixmap(thumb_path)
        if pixmap.isNull():
            # Fallback if thumbnail failed to generate
            self.thumb.setText("No Preview")
            self.thumb.setStyleSheet("background: #333; color: #777;")
        else:
            self.thumb.setPixmap(pixmap.scaled(160, 90, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

        # 2. Episode Info
        self.info = QLabel(f"Episode {ep_number}: {title}")
        self.info.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")

        # 3. Play Button
        self.play_btn = QPushButton("▶ Play")
        self.play_btn.setFixedWidth(80)
        self.play_btn.clicked.connect(lambda: self.clicked.emit(file_path))

        layout.addWidget(self.thumb)
        layout.addWidget(self.info, 1)  # '1' makes it stretch to fill space
        layout.addWidget(self.play_btn)

        self.setStyleSheet("background: #1e1e1e; border-radius: 5px; margin: 2px;")