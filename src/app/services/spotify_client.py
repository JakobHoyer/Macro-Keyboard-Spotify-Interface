from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

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
        app_name: str = "MacroKeyboardSpotifyInterface"
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
    

    def ensure_automatic_logging(self, host="127.0.0.1", port=8888, path="/callback"):
        """
        Upons up the redirect url, and fetches the code and inputs it automatically. The user
        hereby only needs to login in the browser (or press agree).
        It does this with a simple HTTP server that listens for the redirect.
        """
        if self._auth.get_cached_token():
            return

        code_holder = {"code": None}
        done = threading.Event()

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                u = urlparse(self.path)
                if u.path != path:
                    self.send_response(404); self.end_headers(); return
                qs = parse_qs(u.query)
                code_holder["code"] = (qs.get("code") or [None])[0]

                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"<h2>Spotify login OK</h2><p>Du kan lukke dette vindue.</p>")
                done.set()

            def log_message(self, *_):
                pass  # mute console noise
        
        server = HTTPServer((host, port), Handler)

        # Start server in background
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()

        # Open login URL in browser
        login_url = self._auth.get_authorize_url()
        webbrowser.open(login_url)

        # Wait for callback
        done.wait(timeout=180)
        server.shutdown()

        code = code_holder["code"]
        if not code:
            raise RuntimeError("Login timeout eller ingen code modtaget")

        # Exchange the code to token (written in cache_path)
        self._auth.get_access_token(code)


    def get_logged_in_state(self) -> LoginState: 
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
    

    def play_track_auto(self, track_uri: str) -> None:
        """
        Start playback of the given track URI on an available device
        """
        self.play_track(self._pick_device_id(), track_uri)


    def play_playlist(self, device_id: str, playlist_uri: str) -> None:
        """
        Start playback of the given playlist URI on the given device.
        """
        sp = self._ensure_client()
        sp.start_playback(device_id=device_id, context_uri=playlist_uri)


    def play_playlist_auto(self, playlist_uri: str) -> None:
        """
        Start playback of the given playlist URI on an available device.
        """
        self.play_playlist(self._pick_device_id(), playlist_uri)


    def play_uris(self, uris: List[str], device_id: str) -> None:
        """
        Start playback of the given list of URIs on the given device.
        """
        sp = self._ensure_client()
        sp.start_playback(device_id=device_id, uris=uris)


    def play_uris_auto(self, uris: List[str]) -> None:
        """
        Start playback of the given list of URIs on an available device.
        """
        self.play_uris(self._pick_device_id(), uris)


    def pause(self, device_id: Optional[str] = None) -> None:
        """
        Pause playback on the given device.
        """
        sp = self._ensure_client()
        sp.pause_playback(device_id=device_id)


    def pause_auto(self) -> None:
        self.pause(self._pick_device_id())


    def resume(self, device_id: Optional[str] = None) -> None:
        """
        Resume playback on the given device.
        """
        sp = self._ensure_client()
        sp.start_playback(device_id=device_id)
    

    def resume_auto(self) -> None:
        self.resume(self._pick_device_id())


    def toggle_pause_resume(self, device_id: Optional[str] = None) -> None:
        """
        Toggle pause/resume playback on the given device.
        """
        sp = self._ensure_client()
        playback = sp.current_playback()
        is_playing = playback.get("is_playing", False) if isinstance(playback, dict) else False

        if is_playing:
            sp.pause_playback(device_id=device_id)
        else:
            sp.start_playback(device_id=device_id)


    def toggle_pause_resume_auto(self) -> None:
        self.toggle_pause_resume(self._pick_device_id())


    def next(self, device_id: Optional[str] = None) -> None:
        """
        Skip to the next track on the given device.
        """
        sp = self._ensure_client()
        sp.next_track(device_id=device_id)


    def next_auto(self) -> None:
        self.next(self._pick_device_id())


    def previous(self, device_id: Optional[str] = None) -> None:
        """
        Skip to the previous track on the given device.
        """
        sp = self._ensure_client()
        sp.previous_track(device_id=device_id)


    def previou_auto(self) -> None:
        self.previous(self._pick_device_id())


    def logout(self) -> None:
        """
        Logout by deleting the cached token.
        """
        self._sp = None
        try:
            Path(self._cache_path).unlink(missing_ok=True)
        except Exception as e:
            raise RuntimeError(f"Failed to delete cache file: {e}") from e


    def get_song_info(self) -> Optional[dict]:
        """
        Get information about the currently playing song.
        """
        sp = self._ensure_client()
        playback = sp.current_playback()
        if not playback or not isinstance(playback, dict):
            return None
        item = playback.get("item")
        if not item or not isinstance(item, dict):
            return None
        return item


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
    

    def _pick_device_id(self) -> str:
        devices = self.list_devices()
        if not devices:
            raise RuntimeError("No Spotify devices available")
        active = next((d for d in devices if d.is_active), None)
        return (active or devices[0]).id