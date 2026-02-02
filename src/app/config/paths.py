from dataclasses import dataclass
from platformdirs import user_cache_dir, user_config_dir
from pathlib import Path

@dataclass(frozen=True)
class Paths:

    app_name: str = "MacroKeyboardSpotifyInterface"
    app_author: str = "JakobHoyer"

    @property
    def config_dir(self) -> Path:
        return Path(user_config_dir(self.app_name, self.app_author))
    
    @property
    def cache_dir(self) -> Path:
        return Path(user_cache_dir(self.app_name, self.app_author))
    
    @property
    def settings_path(self) -> Path:
        return self.config_dir / "settings.json"

    @property
    def token_cache_path(self) -> Path:
        return self.cache_dir / "spotify_token_cache.json"

    @property
    def covers_dir(self) -> Path:
        return self.cache_dir / "covers"
    
    @property
    def covers_max_size_mb(self) -> int:
        return 100  # Max cache size for covers in MB
    
    def ensure_directories(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.covers_dir.mkdir(parents=True, exist_ok=True)

paths = Paths()