from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap

from app.ui.background_widget import BackgroundWidget
from app.core.actions import Action

class MainWindow(QMainWindow):
    action_requested = Signal(object)  # UI -> controller

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macro Spotify App")

        root = BackgroundWidget("assets/images/knight-at-fire2.png")
        layout = root.layout

        self.status = QLabel("Status: klar")
        self.status.setStyleSheet("color: white;")
        self.error = QLabel("")
        self.error.setStyleSheet("color: red;")

        self.cover = QLabel()
        self.cover.setAlignment(Qt.AlignCenter)
        self.cover.setMinimumHeight(180)  # så den har plads
        layout.addWidget(self.cover)

        btn1 = QPushButton("Play/Pause")
        btn2 = QPushButton("Slot 1")
        btn3 = QPushButton("Slot 2")

        btn1.clicked.connect(lambda: self.action_requested.emit(Action.PLAY_PAUSE))
        btn2.clicked.connect(lambda: self.action_requested.emit(Action.SLOT_1))
        btn3.clicked.connect(lambda: self.action_requested.emit(Action.SLOT_2))

        layout.addWidget(self.status)
        layout.addWidget(self.error)
        layout.addWidget(btn1)
        layout.addWidget(btn2)
        layout.addWidget(btn3)

        self.setCentralWidget(root)
        self._cover_pix = QPixmap()

    def set_status(self, text: str) -> None:
        self.status.setText(f"Status: {text}")

    def set_error(self, text: str) -> None:
        self.error.setText(text)
    
    
    def set_cover(self, pix: QPixmap) -> None:
        self._cover_pix = pix
        self._rescale_cover()

    def resizeEvent(self, e):
        self._rescale_cover()
        super().resizeEvent(e)

    def _rescale_cover(self):
        if self._cover_pix.isNull():
            self.cover.clear()
            return
        self.cover.setPixmap(self._cover_pix.scaled(
            self.cover.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
