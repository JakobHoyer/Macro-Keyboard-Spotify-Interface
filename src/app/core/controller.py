from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, Optional

from .actions import ActionEvent, ActionKind

StatusFn = Callable[[str], None]   # UI kan sætte en status label
ErrorFn  = Callable[[str], None]
CoverUrlFn = Callable[[str], None]  # UI kan sætte cover via URL

@dataclass
class Binding:
    type: str  # "track" / "playlist"
    uri: str
    keybind: str = "" # Optional keybind
    name: str = "" # Optional name for display purposes



class AppController:
    def __init__(
        self,
        spotify_service,
        bindings: Dict[ActionEvent, Binding],
        set_status: StatusFn,
        set_error: ErrorFn,
        set_cover_url: CoverUrlFn,
    ) -> None:
        self.spotify = spotify_service
        self.bindings = bindings
        self.set_status = set_status
        self.set_error = set_error
        self.set_cover_url = set_cover_url
        self._last_cover_url = ""


    def refresh_playback(self) -> None:
        try:
            # change get_cover_url to get_song_info and then make get_cover_url have song as argument.
            song = self.spotify.get_song_info()
            if song:
                self.set_status(f"{song['name']}  -  {song['artists'][0]['name']}")
                url = self.get_cover_url(song)
                if url and url.startswith("http") and url != self._last_cover_url:
                    self.set_cover_url(url)
                    self._last_cover_url = url
        except Exception as e:
            self.set_error(f"Error refreshing playback: {e}")


    def handle_action(self, action: ActionEvent, source: str) -> None:
        try:
            self.set_status(f"Action: {action} (from {source})")

            if action.kind == ActionKind.PLAY_PAUSE:
                self.spotify.toggle_pause_resume()
                return

            if action.kind == ActionKind.NEXT:
                self.spotify.next()
                return

            if action.kind == ActionKind.PREV:
                self.spotify.previous()
                return

            if action.kind == ActionKind.SLOT:
                if action.slot_id is None:
                    return
                binding = self.bindings.get(("slot", action.slot_id))
                if not binding:
                    self.set_error(f"No binding for slot {action.slot_id}")
                    return

                self._play_binding(binding)
                return

        except Exception as e:
            self.set_error(f"Error handling action: {e}")


    def update_bindings(self, new_bindings: Dict[ActionEvent, Binding]) -> None:
        self.bindings = new_bindings


    def get_cover_url(self, song: Optional[dict] = None) -> str:
        if song:
            images = song.get("album", {}).get("images", [])
            if images:
                cover_url = images[0]["url"]  # largest
                return cover_url
        return ""


    def _play_binding(self, binding: Binding) -> None:
        if binding.type == "track":
            self.spotify.play_track(binding.uri)
        elif binding.type == "playlist":
            self.spotify.play_playlist(binding.uri)
        elif binding.type == "uris":
            uris = binding.uri.split(",")
            self.spotify.play_uris(uris)
        # potentially add album here.