from PySide6.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit
from PySide6.QtCore import Qt

from app.services.spotify_client import SpotifyService

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macro Keyboard Spotify Interface")
        container = QWidget()
        self.setCentralWidget(container)
        layout = QVBoxLayout(container)
        button1 = QPushButton("DO IT!")
        button1.clicked.connect(self.on_button1_clicked)
        label1 = QLabel("Rammstein me")
        label1.setAlignment(Qt.AlignCenter)
        layout.addWidget(label1)
        layout.addWidget(button1)

    
    def on_button1_clicked(self) -> None:
        client_id = "4075de68534e4c0c92d89a9c9c21d29f"
        redirect_uri = "http://127.0.0.1:8888/callback"
        scope = "user-read-playback-state user-modify-playback-state"


        svc = SpotifyService(
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope
        )

        svc.ensure_automatic_logging()

        state = svc.get_logged_in_state()

        if not state.is_logged_in:
            print("Please log in:")
            print("Open this URL in your browser:")
            print(state.login_url)
            print("After logging in, paste the redirected URL here:")
            redirected_url = input().strip()
            svc.finish_login(redirected_url)
            state = svc.get_logged_in_state()


        devices = svc.list_devices()
        if not devices:
            print("No active Spotify devices found. Please start Spotify on one of your devices and try again.")
        else:
            svc.play_playlist(devices[0].id, "spotify:playlist:4zqPelMTbUfaSpAKWHux7M")