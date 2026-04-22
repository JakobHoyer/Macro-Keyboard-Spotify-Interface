from enum import Enum


class ActionKind(str, Enum):
    PLAY_PAUSE = "play_pause"
    NEXT = "next"
    PREV = "prev"
    PLAY_SPOTIFY = "play_spotify"