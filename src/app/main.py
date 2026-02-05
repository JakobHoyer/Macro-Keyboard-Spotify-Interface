import sys
import ctypes
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from pathlib import Path

from app.config.settings import Settings
from app.config.paths import paths
from app.ui.main_window import MainWindow
from app.ui.image_loader import ImageLoader
from app.core.controller import AppController
from app.services.spotify_client import SpotifyService
from app.input.hotkeys_pynput import HotkeyBackendPynput


def main():
    set_app_id("JakobHoyer.MacroKeyboardSpotifyInterface")
    app = QApplication(sys.argv)
    # app icon might be redundant with main window icon
    icon_path = Path(__file__).parent.parent.parent / "assets" / "ico" / "lute.ico"
    app.setWindowIcon(QIcon(str(icon_path)))
    window = MainWindow()

    paths.ensure_directories()
    settings = Settings(paths)
    settings.load()

    # image loader
    image_loader = ImageLoader()
    current_cover_url = {"url": ""}
    
    def set_cover_url(url: str) -> None:
        if not url:
            return
        current_cover_url["url"] = url
        image_loader.load(url)

    def on_image_loaded(url, pix):
        if url != current_cover_url["url"]:
            return  # old response
        window.set_cover(pix)

    image_loader.loaded.connect(on_image_loaded)
    image_loader.failed.connect(lambda url, err: print(f"Image load failed for {url}: {err}"))

    # Run services
    spotify = SpotifyService(
        client_id="4075de68534e4c0c92d89a9c9c21d29f",
        redirect_uri="http://127.0.0.1:8888/callback",
        scope="user-read-playback-state user-modify-playback-state",
    )

    control_bindings = settings.get_slot_bindings()

    # Start action and ui controller
    controller = AppController(
        spotify_service=spotify,
        control_bindings=control_bindings,
        set_status=window.set_status,
        set_error=window.set_error,
        set_cover_url=set_cover_url,
    )

    timer = QTimer()
    timer.setInterval(700)
    timer.timeout.connect(controller.refresh_playback)
    timer.timeout.connect(spotify.ensure_automatic_logging)
    timer.start()

    hotkey_bindings = settings.get_hotkey_bindings()
    hotkey_backend = HotkeyBackendPynput(hotkey_bindings)
    hotkey_backend.start(lambda action, source: controller.handle_action(action, source))
    
    # This handles the UI buttons
    window.action_requested.connect(lambda a: controller.handle_action(a, "ui"))

    # show window in background image size
    window.resize(320*3, 180*3)
    window.show()
    
    exit_code = app.exec()

    sys.exit(exit_code)


def set_app_id(app_id: str):
    """Set application user model id for Windows taskbar grouping."""
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception as e:
        pass  # Not Windows or failed


if __name__ == "__main__":
    main()