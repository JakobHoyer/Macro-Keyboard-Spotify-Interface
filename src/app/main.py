import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from app.ui.main_window import MainWindow
from app.ui.image_loader import ImageLoader
from app.core.actions import Action
from app.core.controller import AppController, SlotBinding

# fra dine egne filer
from app.services.spotify_client import SpotifyService
from app.input.fake_serial import FakeSerialBackend
from app.input.hotkeys_pynput import HotkeyBackendPynput
# fra app.input.hotkeys_pynput import HotkeyBackendPynput  # senere på Windows


def main():
    app = QApplication(sys.argv)

    # 1) UI
    window = MainWindow()

    # 2) Spotify service (brug PKCE når du når dertil)
    spotify = SpotifyService(
        client_id="4075de68534e4c0c92d89a9c9c21d29f",
        redirect_uri="http://127.0.0.1:8888/callback",
        scope="user-read-playback-state user-modify-playback-state",
    )


    # Image loader
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



    # 3) Bindings (senere load fra settings.json i AppData)
    bindings = {
        Action.SLOT_1: SlotBinding(type="playlist", uri="spotify:playlist:4zqPelMTbUfaSpAKWHux7M"),
        Action.SLOT_2: SlotBinding(type="track", uri="spotify:track:6woV8uWxn7rcLZxJKYruS1"),
    }

    # 4) Controller
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
    timer.start()


    # 5) Backend (fake serial for Wayland test)
    backend = FakeSerialBackend({
        Action.SLOT_1: "SLOT_1",
        Action.SLOT_2: "SLOT_2",
        Action.PLAY_PAUSE: "PLAY_PAUSE",
    })

    hotkey_backend = HotkeyBackendPynput({
        Action.SLOT_1: "<ctrl>+<alt>+<f1>",
        Action.SLOT_2: "<ctrl>+<alt>+<f2>",
        Action.PLAY_PAUSE: "<ctrl>+<alt>+p",
    })

    backend.start(lambda action, source: controller.handle_action(action, source))
    hotkey_backend.start(lambda action, source: controller.handle_action(action, source))

    # 6) UI -> controller (knapper i UI)
    window.action_requested.connect(lambda a: controller.handle_action(a, "ui"))

    window.show()
    spotify.ensure_automatic_logging()
    exit_code = app.exec()

    backend.stop()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()