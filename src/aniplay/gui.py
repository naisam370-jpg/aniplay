from __future__ import annotations
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
img =