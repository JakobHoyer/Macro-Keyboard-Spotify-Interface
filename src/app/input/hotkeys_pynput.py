from __future__ import annotations
import os
from typing import Callable, Dict
from functools import partial
from pynput import keyboard

from .base import InputBackend
from ..core.actions import ActionEvent


class HotkeyBackendPynput(InputBackend):
    """
    Works well on Windows.
    On Linux it's mainly viable on X11. On Wayland it may not work.
    """

    def __init__(self, bindings: Dict[ActionEvent, str]) -> None:
        """
        bindings example:
          {
            ActionEvent(ActionKind.SLOT, 1): "<ctrl>+<alt>+<f1>",
            ActionEvent(ActionKind.PLAY_PAUSE): "<f13>",
          }
        """
        self._bindings = bindings
        self._listener = None

    def is_supported(self) -> bool:
        if os.name == "nt":
            return True
        # Linux: only reliably on X11
        return os.environ.get("XDG_SESSION_TYPE", "").lower() != "wayland"

    def start(self, emit: Callable[[ActionEvent, str], None]) -> None:
        if not self.is_supported():
            raise RuntimeError("Hotkey backend not supported in this environment")

        hotkey_map = {hotkey: partial(emit, action, "hotkeys") for action, hotkey in self._bindings.items()}

        # GlobalHotKeys expects strings like "<ctrl>+<alt>+p"
        self._listener = keyboard.GlobalHotKeys(hotkey_map)
        self._listener.start()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
            self._listener = None
