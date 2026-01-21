from _ctypes import alignment
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
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
        content = QWidget()
        layout.addWidget(content)

        outer_layout = QHBoxLayout(content)
        outer_layout.setContentsMargins(2, 2, 2, 2)
        
        panel = QWidget()
        buttons_layout = QHBoxLayout()

        self.status = QLabel("Ready")
        self.status.setStyleSheet("color: white;")
        self.status.setWordWrap(True)
        self.status.setAlignment(Qt.AlignCenter)

        self.error = QLabel("")
        self.error.setStyleSheet("color: red;")

        self.cover = QLabel()
        self.cover.setAlignment(Qt.AlignCenter)
        self.cover.setFixedSize(180, 180)

        btn_prev = QPushButton("◀")
        btn_play = QPushButton("⏯")
        btn_next = QPushButton("▶")

        btn_prev.setFixedSize(52, 40)
        btn_play.setFixedSize(68, 40)
        btn_next.setFixedSize(52, 40)

        btn_prev.clicked.connect(lambda: self.action_requested.emit(Action.SLOT_1))
        btn_play.clicked.connect(lambda: self.action_requested.emit(Action.PLAY_PAUSE))
        btn_next.clicked.connect(lambda: self.action_requested.emit(Action.SLOT_2))

        #outer_layout.addStretch(1)
        panel.setFixedWidth(180)
        panel_layout = QVBoxLayout(panel)
        panel_layout.addStretch()
        panel_layout.setSpacing(6)
        panel_layout.setContentsMargins(0, 0, 0, 0)

        buttons_layout.setSpacing(6)
        buttons_layout.addWidget(btn_prev)
        buttons_layout.addWidget(btn_play)
        buttons_layout.addWidget(btn_next)
        buttons_layout.setAlignment(Qt.AlignCenter)

        panel_layout.addWidget(self.status)
        panel_layout.addWidget(self.cover, alignment=Qt.AlignCenter)
        panel_layout.addLayout(buttons_layout)
        outer_layout.addWidget(panel)
        outer_layout.addStretch(1)

        self.setCentralWidget(root)
        self._cover_pix = QPixmap()


    def set_status(self, text: str) -> None:
        self.status.setText(f"{text}")


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
        self.cover.setPixmap(
            self._cover_pix.scaled(
                self.cover.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
        ))
