from PySide6.QtWidgets import QMainWindow, QStackedWidget, QPushButton
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon, QPixmap

from app.ui.widgets.background_widget import BackgroundWidget
from app.ui.player_screen import PlayerScreen
from app.ui.bindings_screen import BindingsScreen
from pathlib import Path

class MainWindow(QMainWindow):
    action_requested = Signal(object)  # UI -> controller

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macro Spotify App")
        root = BackgroundWidget("assets/images/knight-at-fire3.png")
        self.set_icon("assets/ico/lute.ico")
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


    def set_icon(self, image_path: str) -> None:
        proj_dir = Path(__file__).parent.parent.parent # src
        total_path = Path(proj_dir / image_path).as_posix().replace("\\", "/")
        app_icon = QIcon(total_path)
        self.setWindowIcon(app_icon)


    def switch_screen(self) -> None:
        if self.screen.currentWidget() == self.player_screen:
            self.show_bindings_screen()
        else:
            self.show_player_screen()


    def show_player_screen(self) -> None:
        self.screen.setCurrentWidget(self.player_screen)


    def show_bindings_screen(self) -> None:
        self.screen.setCurrentWidget(self.bindings_screen)
