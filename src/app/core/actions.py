from dataclasses import dataclass
from enum import Enum
from typing import Optional

class ActionKind(str, Enum):
    PLAY_PAUSE = "play_pause"
    NEXT = "next"
    PREV = "prev"
    SLOT = "slot"

@dataclass(frozen=True)
class ActionEvent:
    kind: ActionKind
    slot_id: Optional[int] = None
