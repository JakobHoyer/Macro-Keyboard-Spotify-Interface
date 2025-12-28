from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any

import urllib.parse as up

import spotipy
from spotipy.oauth2 import SpotifyPKCE
from platformdirs import user_cache_dir


@dataclass(frozen=True)
class SpotifyDevice:
    id: str
    name: str
    type: str
    is_active: bool
    volume_percent: Optional[int]


@dataclass(frozen=True)
class LoginState:
    is_logged_in: bool
    login_url: Optional[str] = None
    reason: Optional[str] = None


class SpotifyService:
    """
    GUI-friendly wrapper around Spotipy OAuth + playback.

    Typical GUI flow:
      - svc = SpotifyService(...)
      - state = svc.get_login_state()
      - if state.is_logged_in: enable playback buttons
      - else: show "Login" button -> open state.login_url in browser
              then user pastes redirected URL -> svc.finish_login(redirected_url)
    """

    def __init__(
        self, 
        client_id: str,
        redirect_uri: str,
        scope: str,
        app_name: str = "MacroKeyboardSpotify"
    ) -> None:

        self._client_id = client_id
        self._redirect_uri = redirect_uri

        # normalize scope string (no commas)
        self._scope = " ".join([s.strip() for s in scope.replace(",", " ").split()])

        cache_dir = Path(user_cache_dir(app_name))
        cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache_path = str(cache_dir / "spotify_token_cache")

        self._auth = SpotifyPKCE(
            client_id=self._client_id,
            redirect_uri=self._redirect_uri,
            scope=self._scope,
            open_browser=False, # let GUI handle browser opening
            cache_path=self._cache_path,
        )
    
        self._sp: Optional[spotipy.Spotify] = None


    @property
    def cache_path(self) -> str:
        """ Used for debugging token location."""
        return self._cache_path
    

    def get_logged_in_state(self) -> bool:
        """
        Check if user is logged in (i.e. if we have a cached token).
        """
        token = self._auth.get_cached_token()
        if token:
            self._ensure_client()
            return LoginState(is_logged_in=True)
    
        return LoginState(
            is_logged_in=False,
            login_url=self._auth.get_authorize_url(),
            reason="No cached token found."
        )
    
    def finish_login(self, redirected_url: str) -> None:
        """
        Finish loging by using the redirected url from the browser and
        making a cache token, so we dont hace to do it more than once.
        """
        redirected_url = redirected_url.strip()
        if not redirected_url:
            raise ValueError("Redirected URL is an empty string.")
        
        code = self._auth.parse_response_code(redirected_url)
        if not code:
            raise ValueError("Could not parse authorization code from redirected URL.")
        
        token_info = self._auth.get_access_token(code)
        access_token = token_info["access_token"] if isinstance(token_info, dict) else token_info
        
        self._sp = spotipy.Spotify(auth=access_token)
    
    def list_devices(self) -> List[SpotifyDevice]:
        """
        List available Spotify devices.
        """
        sp = self._ensure_client()
        payload = sp.devices()
        devices = payload.get("devices", []) if isinstance(payload, dict) else []
        return [
            SpotifyDevice(
                id=d.get("id", ""),
                name=d.get("name", ""),
                type=d.get("type", ""),
                is_active=bool(d.get("is_active", False)),
                volume_percent=d.get("volume_percent"),
            )
            for d in devices
            if d.get("id")
        ]
    
    def transfer_playback(self, device_id: str, force_play: bool = True) -> None:
        """
        Transfer playback to the given device.
        """
        sp = self._ensure_client()
        sp.transfer_playback(device_id=device_id, force_play=force_play)

    def play_track(self, device_id: str, track_uri: str) -> None:
        """
        Start playback of the given track URI on the given device.
        """
        sp = self._ensure_client()
        sp.start_playback(device_id=device_id, uris=[track_uri])
    
    def play_playlist(self, device_id: str, playlist_uri: str) -> None:
        """
        Start playback of the given playlist URI on the given device.
        """
        sp = self._ensure_client()
        sp.start_playback(device_id=device_id, context_uri=playlist_uri)

    def play_uris(self, uris: List[str], device_id: str) -> None:
        """
        Start playback of the given list of URIs on the given device.
        """
        sp = self._ensure_client()
        sp.start_playback(device_id=device_id, uris=uris)
    
    def pause(self, device_id: Optional[str] = None) -> None:
        """
        Pause playback on the given device.
        """
        sp = self._ensure_client()
        sp.pause_playback(device_id=device_id)

    def resume(self, device_id: Optional[str] = None) -> None:
        """
        Resume playback on the given device.
        """
        sp = self._ensure_client()
        sp.start_playback(device_id=device_id)

    def logout(self) -> None:
        """
        Logout by deleting the cached token.
        """
        self._sp = None
        try:
            Path(self._cache_path).unlink(missing_ok=True)
        except Exception as e:
            raise RuntimeError(f"Failed to delete cache file: {e}") from e


    def _ensure_client(self) -> spotipy.Spotify:
        """
        Ensure that the Spotify client is initialized and has a valid token.
        Uses cached token and refreshes if necessary.
        """
        if self._sp is not None:
            return self._sp

        token_info = self._auth.get_cached_token()
        if not token_info:
            raise RuntimeError("User is not logged in. Call get_login_state() and finish_login() first.")
        
        access_token = token_info["access_token"] if isinstance(token_info, dict) else token_info
        self._sp = spotipy.Spotify(auth=access_token)
        return self._sp