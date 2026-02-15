import json
from typing import Dict
from app.core.actions import ActionEvent, ActionKind
from app.core.controller import Binding
from app.config.paths import Paths

# make an ensure settings exist function, that checks if there is an app data
# file. Make a different function which creates default settings if none exist.

class Settings:
    def __init__(self, paths: Paths):
        self._paths = paths
        self.data = None # type dictionary


    def load(self):
        if not self._paths.settings_path.exists():
            self.data = self.default()
            self.save()
        else:
            with open(self._paths.settings_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
                correct_settigngs: bool = self.ensure_correct_settings()
                if not correct_settigngs:
                    print("Settings have been changed to default values, because some keys were missing.")
                    # we should make a popup.


    def save(self):
        with open(self._paths.settings_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    
    def default(self) -> Dict:
        return {
            "hotkeys": {
                "<ctrl>+<alt>+p": {"kind": "play_pause"},
                "<ctrl>+<alt>+<f1>": {"kind": "slot", "slot_id": 1},
                "<ctrl>+<alt>+<f2>": {"kind": "slot", "slot_id": 2},
            },
            "slots": {
                    "1": {"type": "track", "uri": "spotify:track:6woV8uWxn7rcLZxJKYruS1"},
                    "2": {"type": "playlist", "uri": "spotify:playlist:4zqPelMTbUfaSpAKWHux7M"},
            },
        }


    def ensure_correct_settings(self) -> bool:
        # check if hotkeys and slots are in settings, if not create them with default values
        changed = False
        if "hotkeys" not in self.data:
            self.data["hotkeys"] = self.default()["hotkeys"]
            changed = True
            self.save()
        if "slots" not in self.data:
            self.data["slots"] = self.default()["slots"]
            changed = True
            self.save()
        return changed


    def get_hotkey_bindings(self) -> Dict[ActionEvent, str]:
        converted = {}
        for key, value in self.data["hotkeys"].items():
            kind = value["kind"]
            slot_id = value.get("slot_id")
            action_event = ActionEvent(
                kind=ActionKind(kind),
                slot_id=slot_id
            )
            converted[action_event] = key
        return converted
    

    def get_slot_bindings(self) -> Dict[int, Binding]:
        converted = {}
        for slot_id, slot_info in self.data["slots"].items():
            converted[int(slot_id)] = Binding(
                type=slot_info["type"],
                uri=slot_info["uri"]
            )
        return converted