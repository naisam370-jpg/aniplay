from __future__ import annotations
from pathlib import Path
from typing import List
import sys
import threading

from PyQt6.QtCore import Qt, QSize, QEvent
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QGridLayout, QLabel, QFileDialog,
    QApplication, QHBoxLayout, QPushButton, QMessageBox, QMenuBar, QAction
)

from .config import ensure_config, save_config
from .library import iter_episodes, Episode
from .anilist import fetch_cover_and_title
from .player import Player

THUMB_W, THUMB_H = 220, 330

class PosterLabel(QLabel):
    def __init__(self, index: int):
        super().__init__("")
        self.index = index
        self.setFixedSize(QSize(THUMB_W, THUMB_H))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 2px solid transparent; border-radius: 8px;")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AniPlay")
        self.resize(1280, 800)

        self.cfg = ensure_config()
        self.player = Player(embed_wid=None if not self.cfg.get("use_embedded_mpv") else int(self.winId()))

        menubar = QMenuBar(self)
        file_menu = menubar.addMenu("File")
        open_action = QAction("Add Library Folder", self)
        open_action.triggered.connect(self.add_folder)
        file_menu.addAction(open_action)

        self.layout_main = QVBoxLayout(self)
        self.layout_main.setMenuBar(menubar)

        top = QHBoxLayout()
        self.btn_add = QPushButton("+ Add Folder")
        self.btn_add.clicked.connect(self.add_folder)
        top.addWidget(self.btn_add)
        top.addStretch(1)
        self.layout_main.addLayout(top)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setHorizontalSpacing(16)
        self.grid.setVerticalSpacing(16)
        self.scroll.setWidget(self.container)
        self.layout_main.addWidget(self.scroll, 1)

        self.episodes: List[Episode] = []
        self.labels: List[PosterLabel] = []
        self.selected = 0

        self.reload_library()
        self.update_grid()
        self.highlight()

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.container.installEventFilter(self)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select anime folder")
        if not folder:
            return
        paths = list(self.cfg.get("library_paths", []))
        if folder not in paths:
            paths.append(folder)
            self.cfg["library_paths"] = paths
            save_config(self.cfg)
            self.reload_library()
            self.update_grid()
            self.highlight()

    def reload_library(self):
        paths = [Path(p) for p in self.cfg.get("library_paths", [])]
        self.episodes = iter_episodes(paths)

    def update_grid(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self.labels.clear()

        per_row = int(self.cfg.get("posters_per_row", 6))
        row = col = 0
        for idx, ep in enumerate(self.episodes):
            label = PosterLabel(idx)
            label.setText("Loading...")
            self.grid.addWidget(label, row, col)
            self.labels.append(label)
            threading.Thread(target=self._load_cover_async, args=(idx, ep), daemon=True).start()
            col += 1
            if col >= per_row:
                col = 0
                row += 1

    def _load_cover_async(self, idx: int, ep: Episode):
        title, cover_path = fetch_cover_and_title(ep.path.name)
        def apply():
            lbl = self.labels[idx]
            if cover_path and cover_path.exists():
                img = QImage(str(cover_path))
                pix = QPixmap.fromImage(img).scaled(THUMB_W, THUMB_H, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                lbl.setPixmap(pix)
                lbl.setToolTip(title)
            else:
                lbl.setText(title)
        QApplication.instance().postEvent(self, _LambdaEvent(apply))

    def keyPressEvent(self, e):
        per_row = int(self.cfg.get("posters_per_row", 6))
        if e.key() == Qt.Key.Key_Right:
            if self.selected < len(self.labels) - 1:
                self.selected += 1
        elif e.key() == Qt.Key.Key_Left:
            if self.selected > 0:
                self.selected -= 1
        elif e.key() == Qt.Key.Key_Down:
            self.selected = min(self.selected + per_row, len(self.labels) - 1)
        elif e.key() == Qt.Key.Key_Up:
            self.selected = max(self.selected - per_row, 0)
        elif e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.play_selected()
        elif e.key() == Qt.Key.Key_R:
            self.reload_library()
            self.update_grid()
        self.highlight()
        super().keyPressEvent(e)

    def highlight(self):
        for i, lbl in enumerate(self.labels):
            if i == self.selected:
                lbl.setStyleSheet("border: 4px solid #4da3ff; border-radius: 8px;")
                self.scroll.ensureWidgetVisible(lbl)
            else:
                lbl.setStyleSheet("border: 2px solid transparent; border-radius: 8px;")

    def play_selected(self):
        if not self.labels:
            return
        ep = self.episodes[self.selected]
        try:
            self.player.play(str(ep.path))
        except Exception as ex:
            QMessageBox.critical(self, "MPV Error", str(ex))

    def eventFilter(self, obj, event):
        return super().eventFilter(obj, event)

class _LambdaEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    def __init__(self, fn):
        super().__init__(_LambdaEvent.EVENT_TYPE)
        self.fn = fn

    def execute(self):
        try:
            self.fn()
        except Exception:
            pass

def custom_event_handler(obj, event):
    if isinstance(event, _LambdaEvent):
        event.execute()
        return True
    return False

def main():
    app = QApplication(sys.argv)
    # install custom event handler
    QApplication.instance = QApplication
    QApplication.customEvent = custom_event_handler
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
