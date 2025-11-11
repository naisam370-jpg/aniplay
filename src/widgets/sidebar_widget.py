from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt

class SidebarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(180) # Fixed width for the sidebar
        self.setStyleSheet("background-color: #3a3a3a; border-right: 1px solid #555;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignTop)

        self.btn_library = QPushButton("Library")
        self.btn_search = QPushButton("Search")
        self.btn_settings = QPushButton("Settings")

        layout.addWidget(self.btn_library)
        layout.addWidget(self.btn_search)
        layout.addStretch() # Pushes buttons to the top
        layout.addWidget(self.btn_settings)
