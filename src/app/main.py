import sys
from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow
from app.ui.image_loader import ImageLoader
from app.core.actions import Action
from app.core.controller import AppController, SlotBinding

# fra dine egne filer
from app.services.spotify_client import SpotifyService
from app.input.fake_serial import FakeSerialBackend
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
    image_loader.loaded.connect(lambda url, pix: window.set_cover(pix))
    image_loader.failed.connect(lambda url, err: print(f"Image load failed for {url}: {err}"))
    
    def set_cover_url(url: str) -> None:
        image_loader.load(url)


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

    # 5) Backend (fake serial for Wayland test)
    backend = FakeSerialBackend({
        "SLOT_1": Action.SLOT_1,
        "SLOT_2": Action.SLOT_2,
        "PLAY_PAUSE": Action.PLAY_PAUSE,
    })
    backend.start(lambda action, source: controller.handle_action(action, source))

    # 6) UI -> controller (knapper i UI)
    window.action_requested.connect(lambda a: controller.handle_action(a, "ui"))

    # BONUS: knyt fake serial injection til UI test (du kan lave en knap senere)
    #backend.inject("SLOT_1")

    window.show()
    exit_code = app.exec()

    backend.stop()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()