from enum import Enum

class Action(str, Enum):
    PLAY_PAUSE = "play_pause"
    NEXT = "next"
    PREV = "prev"
    SLOT_1 = "slot_1"
    SLOT_2 = "slot_2"
