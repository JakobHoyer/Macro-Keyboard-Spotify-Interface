from __future__ import annotations
from typing import Callable
from .actions import ActionEvent, Action


class ActionRouter:
    def __init__(self, on_action: Callable[[ActionEvent], None]) -> None:
        self._on_action = on_action

    def emit(self, action: Action, source: str) -> None:
        self._on_action(ActionEvent(action=action, source=source))
