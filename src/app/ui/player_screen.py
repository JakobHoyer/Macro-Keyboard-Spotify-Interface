from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap

from app.core.actions import ActionKind
from app.core.binding_model import BindingModel
from app.ui.widgets.pixel_art_button import PixelArtButton


class PlayerScreen(QWidget):
    action_requested = Signal(object)

    def __init__(self):
        super().__init__()

        self.status = QLabel("Ready")
        self.status.setStyleSheet("color: white;")
        self.status.setWordWrap(True)
        self.status.setAlignment(Qt.AlignCenter)

        self.error = QLabel("")
        self.error.setStyleSheet("color: red;")

        self.cover = QLabel()
        self.cover.setAlignment(Qt.AlignCenter)
        self.cover.setFixedSize(180, 180)

        btn_prev = PixelArtButton(
            "src/assets/images/base_button.png",
            "src/assets/images/base_button_hover.png",
            "src/assets/images/base_button_pressed.png",
            padding=0,
            integer_scale=False,
        )
        btn_play = PixelArtButton(
            "src/assets/images/base_button.png",
            "src/assets/images/base_button_hover.png",
            "src/assets/images/base_button_pressed.png",
            padding=0,
            integer_scale=False,
        )
        btn_next = PixelArtButton(
            "src/assets/images/base_button.png",
            "src/assets/images/base_button_hover.png",
            "src/assets/images/base_button_pressed.png",
            padding=0,
            integer_scale=False,
        )

        btn_prev.setFixedSize(52, 52)
        btn_play.setFixedSize(52, 52)
        btn_next.setFixedSize(52, 52)

        btn_prev.clicked.connect(
            lambda: self.action_requested.emit(
                BindingModel.new_system("Previous song", ActionKind.PREV)
            )
        )
        btn_play.clicked.connect(
            lambda: self.action_requested.emit(
                BindingModel.new_system("Play / Pause", ActionKind.PLAY_PAUSE)
            )
        )
        btn_next.clicked.connect(
            lambda: self.action_requested.emit(
                BindingModel.new_system("Next song", ActionKind.NEXT)
            )
        )

        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(1, 1, 1, 1)

        panel = QWidget()
        buttons_layout = QHBoxLayout()

        panel.setFixedWidth(180)
        panel_layout = QVBoxLayout(panel)
        panel_layout.addStretch(1)
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
                Qt.SmoothTransformation,
            )
        )