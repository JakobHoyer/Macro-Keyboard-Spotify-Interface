from __future__ import annotations
from typing import Callable, Optional

from app.core.actions import ActionKind
from app.core.binding_model import BindingModel

StatusFn = Callable[[str], None]
ErrorFn = Callable[[str], None]
CoverUrlFn = Callable[[str], None]


class AppController:
    def __init__(
        self,
        spotify_service,
        set_status: StatusFn,
        set_error: ErrorFn,
        set_cover_url: CoverUrlFn,
    ) -> None:
        self.spotify = spotify_service
        self.set_status = set_status
        self.set_error = set_error
        self.set_cover_url = set_cover_url
        self._last_cover_url = ""

    def refresh_playback(self) -> None:
        try:
            song = self.spotify.get_song_info()
            if song:
                self.set_status(f"{song['name']}  -  {song['artists'][0]['name']}")
                url = self.get_cover_url(song)
                if url and url.startswith("http") and url != self._last_cover_url:
                    self.set_cover_url(url)
                    self._last_cover_url = url
        except Exception as e:
            self.set_error(f"Error refreshing playback: {e}")

    def handle_binding(self, binding: BindingModel, source: str) -> None:
        try:
            if binding.kind == ActionKind.PLAY_PAUSE:
                self.spotify.toggle_pause_resume_auto()
                return

            if binding.kind == ActionKind.NEXT:
                self.spotify.next_auto()
                return

            if binding.kind == ActionKind.PREV:
                self.spotify.previous_auto()
                return

            if binding.kind == ActionKind.PLAY_SPOTIFY:
                if not binding.uri:
                    self.set_error(f"No Spotify URI for binding: {binding.name}")
                    return

                self._play_binding(binding)
                return

        except Exception as e:
            self.set_error(f"Error handling binding: {e}")

    def get_cover_url(self, song: Optional[dict] = None) -> str:
        if song:
            images = song.get("album", {}).get("images", [])
            if images:
                return images[0]["url"]
        return ""

    def _play_binding(self, binding: BindingModel) -> None:
        if binding.target_type == "track":
            self.spotify.play_track_auto(binding.uri)
        elif binding.target_type == "playlist":
            self.spotify.play_playlist_auto(binding.uri)
        elif binding.target_type == "uris":
            uris = [item.strip() for item in binding.uri.split(",") if item.strip()]
            self.spotify.play_uris_auto(uris)
        else:
            self.set_error(f"Unknown target type: {binding.target_type}")