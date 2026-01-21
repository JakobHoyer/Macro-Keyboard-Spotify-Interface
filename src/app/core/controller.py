from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict

from .actions import Action

StatusFn = Callable[[str], None]   # UI kan sætte en status label
ErrorFn  = Callable[[str], None]
CoverUrlFn = Callable[[str], None]  # UI kan sætte cover via URL

@dataclass
class SlotBinding:
    type: str  # "track" / "playlist"
    uri: str

class AppController:
    def __init__(
        self,
        spotify_service,
        bindings: Dict[Action, SlotBinding],
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


    def handle_action(self, action: Action, source: str) -> None:
        try:
            self.set_status(f"Action: {action} (from {source})")

            if action == Action.PLAY_PAUSE:
                self.spotify.toggle_pause_resume()
                return

            if action in (Action.SLOT_1, Action.SLOT_2):
                binding = self.bindings.get(action)
                if not binding:
                    self.set_error(f"No binding for {action}")
                    return

                # Sørg for at vi har device og den er aktiv (du kan gøre det smartere senere)
                devices = self.spotify.list_devices()

                if binding.type == "track":
                    self.spotify.play_track(devices[0].id, str(binding.uri))
                elif binding.type == "playlist":
                    self.spotify.play_playlist(devices[0].id, str(binding.uri))
                else:
                    self.set_error(f"Unknown binding type: {binding.type}")
                return

            if action == Action.NEXT:
                self.spotify.next_track()
                return

            if action == Action.PREV:
                self.spotify.prev_track()
                return

        except Exception as e:
            self.set_error(f"Error handling action: {e}")


    def get_cover_url(self, song: Optional[dict] = None) -> str:
        if song:
            images = song.get("album", {}).get("images", [])
            if images:
                cover_url = images[0]["url"]  # largest
                return cover_url
        return ""
