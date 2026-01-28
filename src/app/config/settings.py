import json
from typing import Dict


# make an ensure settings exist function, that checks if there is an app data
# file. Make a different function which creates default settings if none exist.



def load_settings(file_path: str) -> Dict:
    """
    Loads settings from a JSON file and returns a dictionary
    with user inputted bindings and settings.
    """
    return json.load(open(file_path))


def save_settings(file_path: str, settings: Dict) -> None:
    """
    Saves settings to a JSON file from a dictionary
    with user inputted bindings and settings.
    """
    json.dump(settings, open(file_path, "w"), indent=4)


def get_default_settings() -> Dict:
    """
    Returns a dictionary with default settings.
    """
    return {
        "bindings": [
                {"slot_id": 1, "type": "playlist", "uri": "spotify:playlist:4zqPelMTbUfaSpAKWHux7M"},
                {"slot_id": 2, "type": "track", "uri": "spotify:track:6woV8uWxn7rcLZxJKYruS1"},
            ],
    }