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

    def handle_action(self, action: Action, source: str) -> None:
        try:
            self.set_status(f"Action: {action} (from {source})")

            if action == Action.PLAY_PAUSE:
                self.spotify.toggle_pause_resume()
                url = self.get_cover_url()
                if url and url.startswith("http"):
                    self.set_cover_url(url)
                return

            if action in (Action.SLOT_1, Action.SLOT_2):
                binding = self.bindings.get(action)
                if not binding:
                    self.set_error(f"Ingen binding for {action}")
                    return

                # Sørg for at vi har device og den er aktiv (du kan gøre det smartere senere)
                devices = self.spotify.list_devices()

                if binding.type == "track":
                    self.spotify.play_track(devices[0].id, binding.uri)
                    self.set_cover_url(self.get_cover_url())
                elif binding.type == "playlist":
                    self.spotify.play_playlist(devices[0].id, str(binding.uri))
                    url = self.get_cover_url()
                    if url and url.startswith("http"):
                        self.set_cover_url(url)
                else:
                    self.set_error(f"Ukendt binding type: {binding.type}")
                return

            if action == Action.NEXT:
                self.spotify.next_track()
                url = self.get_cover_url()
                if url and url.startswith("http"):
                    self.set_cover_url(url)
                return

            if action == Action.PREV:
                self.spotify.prev_track()
                url = self.get_cover_url()
                if url and url.startswith("http"):
                    self.set_cover_url(url)
                return

        except Exception as e:
            self.set_error(f"Fejl: {e}")

    def get_cover_url(self) -> str:
        song = self.spotify.get_song_info()
        if song:
            images = song.get("album", {}).get("images", [])
            if images:
                cover_url = images[0]["url"]  # største
                print(f"Cover URL: {cover_url}")
                return cover_url
        return ""
