from PySide6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap

from app.ui.widgets.background_widget import BackgroundWidget
from app.ui.player_screen import PlayerScreen
from app.ui.bindings_screen import BindingsScreen
from app.core.actions import ActionEvent, ActionKind

class MainWindow(QMainWindow):
    action_requested = Signal(object)  # UI -> controller

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macro Spotify App")

        root = BackgroundWidget("assets/images/knight-at-fire2.png")
        self.setCentralWidget(root)

        change_screen_button = QPushButton("Switch")
        change_screen_button.setFixedSize(50, 42)
        change_screen_button.clicked.connect(self.switch_screen)
        root.layout.addWidget(change_screen_button, alignment=Qt.AlignTop | Qt.AlignRight)

        self.screen = QStackedWidget()
        root.layout.addWidget(self.screen)

        self.player_screen = PlayerScreen()
        self.screen.addWidget(self.player_screen)

        self.bindings_screen = BindingsScreen()
        self.screen.addWidget(self.bindings_screen)

        self.player_screen.action_requested.connect(self.action_requested.emit)


    def set_status(self, text: str) -> None:
        self.player_screen.set_status(f"{text}")


    def set_error(self, text: str) -> None:
        self.player_screen.set_error(text)


    def set_cover(self, pix: QPixmap) -> None:
        self.player_screen.set_cover(pix)


    def switch_screen(self) -> None:
        if self.screen.currentWidget() == self.player_screen:
            self.show_bindings_screen()
        else:
            self.show_player_screen()

    def show_player_screen(self) -> None:
        self.screen.setCurrentWidget(self.player_screen)

    def show_bindings_screen(self) -> None:
        self.screen.setCurrentWidget(self.bindings_screen)
