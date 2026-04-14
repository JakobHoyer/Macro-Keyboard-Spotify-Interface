from dataclasses import dataclass
from typing import Optional

@dataclass
class BindingModel:
    hotkey: str
    kind: str
    slot_id: int | None = None
    slot_type: str = ""
    uri: str = ""