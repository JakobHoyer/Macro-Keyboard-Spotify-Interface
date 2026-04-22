import json
from typing import Dict

from app.config.paths import Paths
from app.core.actions import ActionKind
from app.core.binding_model import BindingModel


class Settings:
    def __init__(self, paths: Paths):
        self._paths = paths
        self.data = None

    def load(self):
        if not self._paths.settings_path.exists():
            self.data = self.default()
            self.save()
            return

        with open(self._paths.settings_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        if self.ensure_correct_settings():
            print("Settings were migrated or corrected.")
            self.save()

    def save(self):
        with open(self._paths.settings_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def default(self) -> Dict:
        return {
            "bindings": [
                {
                    "name": "Play / Pause",
                    "hotkey": "<ctrl>+<alt>+p",
                    "kind": "play_pause",
                    "target_type": "",
                    "uri": "",
                },
                {
                    "name": "Example track",
                    "hotkey": "<ctrl>+<alt>+<f1>",
                    "kind": "play_spotify",
                    "target_type": "track",
                    "uri": "spotify:track:6woV8uWxn7rcLZxJKYruS1",
                },
                {
                    "name": "Example playlist",
                    "hotkey": "<ctrl>+<alt>+<f2>",
                    "kind": "play_spotify",
                    "target_type": "playlist",
                    "uri": "spotify:playlist:4zqPelMTbUfaSpAKWHux7M",
                },
            ]
        }

    def ensure_correct_settings(self) -> bool:
        changed = False

        if "bindings" not in self.data:
            if "hotkeys" in self.data or "slots" in self.data:
                self.data["bindings"] = self._migrate_old_settings()
            else:
                self.data["bindings"] = self.default()["bindings"]
            changed = True

        if "hotkeys" in self.data:
            del self.data["hotkeys"]
            changed = True

        if "slots" in self.data:
            del self.data["slots"]
            changed = True

        normalized = []
        for raw in self.data.get("bindings", []):
            model = BindingModel.from_dict(raw)
            normalized.append(model.to_dict())
            if raw != model.to_dict():
                changed = True

        self.data["bindings"] = normalized
        return changed

    def _migrate_old_settings(self) -> list[dict]:
        migrated = []
        hotkeys = self.data.get("hotkeys", {})
        slots = self.data.get("slots", {})

        for hotkey, action in hotkeys.items():
            old_kind = action.get("kind", "")

            if old_kind == "slot":
                slot_id = action.get("slot_id")
                slot = slots.get(str(slot_id), {})
                migrated.append(
                    BindingModel.from_dict(
                        {
                            "name": slot.get("name", f"Binding {slot_id}"),
                            "hotkey": hotkey,
                            "kind": ActionKind.PLAY_SPOTIFY.value,
                            "target_type": slot.get("type", "track"),
                            "uri": slot.get("uri", ""),
                        }
                    ).to_dict()
                )
            else:
                try:
                    kind = ActionKind(old_kind)
                except ValueError:
                    kind = ActionKind.PLAY_PAUSE

                migrated.append(
                    BindingModel.from_dict(
                        {
                            "name": self._default_name_for_kind(kind),
                            "hotkey": hotkey,
                            "kind": kind.value,
                            "target_type": "",
                            "uri": "",
                        }
                    ).to_dict()
                )

        return migrated

    def _default_name_for_kind(self, kind: ActionKind) -> str:
        mapping = {
            ActionKind.PLAY_PAUSE: "Play / Pause",
            ActionKind.NEXT: "Next song",
            ActionKind.PREV: "Previous song",
            ActionKind.PLAY_SPOTIFY: "Spotify binding",
        }
        return mapping.get(kind, "Binding")

    def get_bindings(self) -> list[BindingModel]:
        return [
            BindingModel.from_dict(item)
            for item in self.data.get("bindings", [])
        ]

    def set_bindings(self, bindings: list[BindingModel]) -> None:
        self.data["bindings"] = [binding.to_dict() for binding in bindings]

    def get_hotkey_bindings(self) -> dict[str, BindingModel]:
        return {
            binding.hotkey: binding
            for binding in self.get_bindings()
            if binding.hotkey.strip()
        }