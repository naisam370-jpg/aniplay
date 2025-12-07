from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal
from .ui_sidebar_widget import Ui_Form as Ui_SidebarWidget

class SidebarWidget(QWidget, Ui_SidebarWidget):
    refresh_requested = Signal() # New signal

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setFixedWidth(180) # Fixed width for the sidebar
        self.setStyleSheet("background-color: #3a3a3a; border-right: 1px solid #555;")

        # Connect the new refresh button
        self.btn_refresh.clicked.connect(self.refresh_requested.emit)
