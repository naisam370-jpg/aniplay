import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QStackedWidget
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize

LIBRARY_PATH = "/home/anime"  # change this to your anime folder
THUMBNAIL_CACHE = os.path.expanduser("~/.aniplay_thumbs")


def ensure_thumbnail(video_path):
    """Ensure a thumbnail exists for the video, return its path."""
    os.makedirs(THUMBNAIL_CACHE, exist_ok=True)
    base = os.path.basename(video_path)
    thumb_path = os.path.join(THUMBNAIL_CACHE, base + ".jpg")

    if not os.path.exists(thumb_path):
        try:
            # Grab a frame at 10 seconds as preview
            subprocess.run([
                "ffmpeg", "-y", "-ss", "00:00:10",
                "-i", video_path,
                "-frames:v", "1",
                "-vf", "scale=320:-1",
                thumb_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print("Thumbnail generation failed:", e)

    return thumb_path if os.path.exists(thumb_path) else None


class AnimeBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AniPlay")
        self.setGeometry(200, 200, 1000, 700)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.mainPage = self.createLibraryPage()
        self.stack.addWidget(self.mainPage)

        self.show()

    def createLibraryPage(self):
        """Shows list of series (folder names)."""
        page = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Select a Series")
        label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(label)

        self.seriesList = QListWidget()
        self.seriesList.setViewMode(QListWidget.ViewMode.ListMode)

        for folder in os.listdir(LIBRARY_PATH):
            folder_path = os.path.join(LIBRARY_PATH, folder)
            if os.path.isdir(folder_path):
                item = QListWidgetItem(folder)
                self.seriesList.addItem(item)

        self.seriesList.itemActivated.connect(self.openSeries)
        layout.addWidget(self.seriesList)

        page.setLayout(layout)
        return page

    def openSeries(self, item):
        """Opens the episode grid inside the folder."""
        series_name = item.text()
        series_path = os.path.join(LIBRARY_PATH, series_name)

        page = QWidget()
        layout = QVBoxLayout()

        label = QLabel(f"Episodes in {series_name}")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)

        self.episodeGrid = QListWidget()
        self.episodeGrid.setViewMode(QListWidget.ViewMode.IconMode)   # <-- show grid
        self.episodeGrid.setIconSize(QSize(240, 135))                 # 16:9 thumbnails
        self.episodeGrid.setGridSize(QSize(260, 180))                 # spacing
        self.episodeGrid.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.episodeGrid.setMovement(QListWidget.Movement.Static)
        self.episodeGrid.setSpacing(10)
        self.episodeGrid.setUniformItemSizes(True)
        self.episodeGrid.setWordWrap(True)
        self.episodeGrid.setWrapping(True)
        self.episodeGrid.setFlow(QListWidget.Flow.LeftToRight)
        self.episodeGrid.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        for file in os.listdir(series_path):
            if file.endswith((".mp4", ".mkv", ".avi")):
                filepath = os.path.join(series_path, file)
                thumb = ensure_thumbnail(filepath)
                item = QListWidgetItem(file)
                if thumb:
                    item.setIcon(QIcon(thumb))
                self.episodeGrid.addItem(item)

        self.episodeGrid.itemActivated.connect(
            lambda ep: self.playEpisode(series_path, ep.text())
        )
        layout.addWidget(self.episodeGrid)

        page.setLayout(layout)
        self.stack.addWidget(page)
        self.stack.setCurrentWidget(page)

    def playEpisode(self, path, filename):
        """Launch mpv to play the selected episode."""
        filepath = os.path.join(path, filename)
        subprocess.Popen(["mpv", filepath])

    def keyPressEvent(self, event):
        """Keyboard navigation + back handling."""
        if event.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Escape):
            if self.stack.currentIndex() > 0:
                self.stack.setCurrentIndex(self.stack.currentIndex() - 1)
        super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnimeBrowser()
    sys.exit(app.exec())
