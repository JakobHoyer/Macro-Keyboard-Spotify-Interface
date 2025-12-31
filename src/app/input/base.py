from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable
from app.core.actions import Action

class InputBackend(ABC):
    @abstractmethod
    def start(self, emit: Callable[[Action, str], None]) -> None: ...
    @abstractmethod
    def stop(self) -> None: ...
    @abstractmethod
    def is_supported(self) -> bool: ...
