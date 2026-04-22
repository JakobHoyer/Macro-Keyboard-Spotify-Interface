from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable

from app.core.binding_model import BindingModel


class InputBackend(ABC):
    @abstractmethod
    def start(self, emit: Callable[[BindingModel, str], None]) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    def is_supported(self) -> bool: ...