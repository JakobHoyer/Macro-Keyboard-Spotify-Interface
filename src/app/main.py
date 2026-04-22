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

    paths.ensure_directories()
    settings = Settings(paths)
    settings.load()

    icon_path = Path(__file__).parent.parent.parent / "assets" / "ico" / "lute.ico"
    app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow(settings)

    image_loader = ImageLoader()
    current_cover_url = {"url": ""}

    def set_cover_url(url: str) -> None:
        if not url:
            return
        current_cover_url["url"] = url
        image_loader.load(url)

    def on_image_loaded(url, pix):
        if url != current_cover_url["url"]:
            return
        window.set_cover(pix)

    image_loader.loaded.connect(on_image_loaded)
    image_loader.failed.connect(lambda url, err: print(f"Image load failed for {url}: {err}"))

    spotify = SpotifyService(
        client_id="4075de68534e4c0c92d89a9c9c21d29f",
        redirect_uri="http://127.0.0.1:8888/callback",
        scope="user-read-playback-state user-modify-playback-state",
    )

    controller = AppController(
        spotify_service=spotify,
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
    hotkey_backend.start(lambda binding, source: controller.handle_binding(binding, source))

    window.set_runtime_dependencies(controller, hotkey_backend)
    window.bindings_screen.bindingsChanged.connect(window.reload_bindings)

    window.action_requested.connect(lambda binding: controller.handle_binding(binding, "ui"))

    window.resize(320 * 3, 180 * 3)
    window.show()

    exit_code = app.exec()
    sys.exit(exit_code)


def set_app_id(app_id: str):
    """Set application user model id for Windows taskbar grouping."""
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass


if __name__ == "__main__":
    main()