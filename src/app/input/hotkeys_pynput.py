from __future__ import annotations
import os
from typing import Callable
from functools import partial

from pynput import keyboard

from .base import InputBackend
from ..core.binding_model import BindingModel


class HotkeyBackendPynput(InputBackend):
    """
    Works well on Windows.
    On Linux it's mainly viable on X11. On Wayland it may not work.
    """

    def __init__(self, bindings: dict[str, BindingModel]) -> None:
        """
        bindings example:
          {
            "<ctrl>+<alt>+<f1>": BindingModel(...),
            "<ctrl>+<alt>+p": BindingModel(...),
          }
        """
        self._bindings = bindings
        self._listener = None

    def is_supported(self) -> bool:
        if os.name == "nt":
            return True
        return os.environ.get("XDG_SESSION_TYPE", "").lower() != "wayland"

    def start(self, emit: Callable[[BindingModel, str], None]) -> None:
        if not self.is_supported():
            raise RuntimeError("Hotkey backend not supported in this environment")

        hotkey_map = {
            hotkey: partial(emit, binding, "hotkeys")
            for hotkey, binding in self._bindings.items()
        }

        self._listener = keyboard.GlobalHotKeys(hotkey_map)
        self._listener.start()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
            self._listener = None