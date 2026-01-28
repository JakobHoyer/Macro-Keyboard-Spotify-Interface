import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from app.ui.main_window import MainWindow
from app.ui.image_loader import ImageLoader
from app.core.actions import ActionEvent
from app.core.controller import AppController, Binding
from app.services.spotify_client import SpotifyService
from app.input.fake_serial import FakeSerialBackend
from app.input.hotkeys_pynput import HotkeyBackendPynput


def main():
    app = QApplication(sys.argv)
    window = MainWindow()

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
    spotify.ensure_automatic_logging # login

    # Setup bindings. This will be done from a settings / binding window later
    bindings = {
        (ActionEvent.SLOT, 1): Binding(type="playlist", uri="spotify:playlist:4zqPelMTbUfaSpAKWHux7M"),
        (ActionEvent.SLOT, 2): Binding(type="track", uri="spotify:track:6woV8uWxn7rcLZxJKYruS1"),
    }


    # Start action and ui controller
    controller = AppController(
        spotify_service=spotify,
        bindings=bindings,
        set_status=window.set_status,
        set_error=window.set_error,
        set_cover_url=set_cover_url,
    )

    timer = QTimer()
    timer.setInterval(700)
    timer.timeout.connect(controller.refresh_playback)
    timer.timeout.connect(spotify.ensure_automatic_logging)
    timer.start()

    # Start backends
    backend = FakeSerialBackend({ # These should be redefined later from bindings
        (ActionEvent.SLOT, 1): "SLOT_1",
        (ActionEvent.SLOT, 2): "SLOT_2",
        ActionEvent.PLAY_PAUSE: "PLAY_PAUSE",
        ActionEvent.NEXT: "NEXT",
        ActionEvent.PREV: "PREV",
    })

    hotkey_backend = HotkeyBackendPynput({ # These should be redefined later from bindings
        (ActionEvent.SLOT, 1): "<ctrl>+<alt>+<f1>",
        (ActionEvent.SLOT, 2): "<ctrl>+<alt>+<f2>",
        ActionEvent.PLAY_PAUSE: "<ctrl>+<alt>+p",
        ActionEvent.NEXT: "<ctrl>+<alt>+right",
        ActionEvent.PREV: "<ctrl>+<alt>+left",
    })

    backend.start(lambda action, source: controller.handle_action(action, source))
    hotkey_backend.start(lambda action, source: controller.handle_action(action, source))

    # Connect UI to the fake serial backend
    window.action_requested.connect(lambda a: controller.handle_action(a, "ui"))
    
    # show window in background image size
    window.resize(320*3, 180*3)
    window.show()
    
    exit_code = app.exec()

    backend.stop()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()