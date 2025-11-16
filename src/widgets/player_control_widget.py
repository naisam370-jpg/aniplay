from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt
from .ui_player_control_widget import Ui_Form as Ui_PlayerControlWidget

class PlayerControlWidget(QWidget, Ui_PlayerControlWidget):
    def __init__(self, mpv_player, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
        self.mpv_player = mpv_player
        self.current_video_data = None

        self.setFixedHeight(60) # Fixed height for the control bar
        self.setStyleSheet("background-color: #282828; border-top: 1px solid #555;")


    def update_info(self, anime_data):
        """Updates the 'Now Playing' label with the current video info."""
        self.current_video_data = anime_data
        title = anime_data.get("title", "Unknown Title")
        episode = anime_data.get("episode")
        display_text = f"Now Playing: {title}"
        if episode is not None:
            display_text += f" - Ep {episode}"
        self.now_playing_label.setText(display_text)

    def on_stop_clicked(self):
        """Stops the video and hides this widget."""
        self.mpv_player.stop()
        self.hide()
        self.now_playing_label.setText("Nothing playing")
