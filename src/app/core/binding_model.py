from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from app.core.actions import ActionKind


@dataclass
class BindingModel:
    id: str
    name: str
    hotkey: str
    kind: ActionKind
    target_type: str = ""
    uri: str = ""

    @classmethod
    def new_user(cls) -> "BindingModel":
        return cls(
            id=str(uuid4()),
            name="New binding",
            hotkey="",
            kind=ActionKind.PLAY_SPOTIFY,
            target_type="track",
            uri="",
        )

    @classmethod
    def new_system(cls, name: str, kind: ActionKind) -> "BindingModel":
        return cls(
            id=f"system:{kind.value}",
            name=name,
            hotkey="",
            kind=kind,
            target_type="",
            uri="",
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BindingModel":
        kind_value = data.get("kind", ActionKind.PLAY_SPOTIFY.value)

        try:
            kind = kind_value if isinstance(kind_value, ActionKind) else ActionKind(kind_value)
        except ValueError:
            kind = ActionKind.PLAY_SPOTIFY

        return cls(
            id=data.get("id", str(uuid4())),
            name=data.get("name", "Binding"),
            hotkey=data.get("hotkey", ""),
            kind=kind,
            target_type=data.get("target_type", ""),
            uri=data.get("uri", ""),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "hotkey": self.hotkey,
            "kind": self.kind.value,
            "target_type": self.target_type,
            "uri": self.uri,
        }