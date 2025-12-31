from __future__ import annotations
import threading
import queue
from typing import Callable, Dict, Optional

from .base import InputBackend
from app.core.actions import Action


class FakeSerialBackend(InputBackend):
    """
    Simulerer en serial enhed:
    - du kan kalde backend.inject("SLOT_1") fra GUI/test
    - backend oversætter til Action og emitter
    """

    def __init__(self, mapping: Dict[str, Action]) -> None:
        self._mapping = mapping
        self._emit: Optional[Callable[[Action, str], None]] = None
        self._q: "queue.Queue[str]" = queue.Queue()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def is_supported(self) -> bool:
        return True

    def start(self, emit: Callable[[Action, str], None]) -> None:
        self._emit = emit
        self._stop.clear()

        def run():
            while not self._stop.is_set():
                try:
                    line = self._q.get(timeout=0.2)
                except queue.Empty:
                    continue
                line = line.strip()
                action = self._mapping.get(line)
                if action and self._emit:
                    self._emit(action, "fake_serial")

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def inject(self, line: str) -> None:
        """Simuler at serial modtager en linje."""
        self._q.put(line)
