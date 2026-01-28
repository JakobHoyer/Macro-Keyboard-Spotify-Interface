from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable
from app.core.actions import ActionEvent

class InputBackend(ABC):
    @abstractmethod
    def start(self, emit: Callable[[ActionEvent, str], None]) -> None: ...
    @abstractmethod
    def stop(self) -> None: ...
    @abstractmethod
    def is_supported(self) -> bool: ...
