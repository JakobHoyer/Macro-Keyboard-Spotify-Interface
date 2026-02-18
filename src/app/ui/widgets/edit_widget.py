from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from app.ui.widgets.binding_widget import BindingWidget
from app.config.settings import Settings

class EditWidget(QWidget):
    def __init__(self, binding_widget: BindingWidget, settings: Settings, on_saved, on_cancel, on_delete):
        super().__init__()
        self._settings = settings
        self._binding = binding_widget
        self._on_saved = on_saved
        self._on_cancel = on_cancel
        self._on_delete = on_delete

        self.layout = QVBoxLayout(self)

        self._old_hotkey = self._binding._hotkey
        hotkey_label = QLabel("Hotkey:")
        hotkey_label.setStyleSheet("color: white;")
        self.layout.addWidget(hotkey_label)
        self.hotkey_input = QLineEdit(self._binding._hotkey)
        self.layout.addWidget(self.hotkey_input)

        action_label = QLabel("Action kind:")
        action_label.setStyleSheet("color: white;")
        self.layout.addWidget(action_label)
        self.kind_input = QLineEdit(self._binding._action.get("kind", ""))
        self.layout.addWidget(self.kind_input)

        slot_id_label = QLabel("Slot id:")
        slot_id_label.setStyleSheet("color: white;")
        self.layout.addWidget(slot_id_label)
        self.slot_id_input = QLineEdit(str(self._binding._action.get("slot_id", "")))
        self.layout.addWidget(self.slot_id_input)

        spotify_uri_label = QLabel("Spotify URI:")
        spotify_uri_label.setStyleSheet("color: white;")
        self.layout.addWidget(spotify_uri_label)
        slot_id = self._binding._action.get("slot_id")
        uri = ""
        if slot_id is not None:
            slot = self._binding._slots.get(str(slot_id))
            if slot:
                uri = slot.get("uri", "")
        self.uri_input = QLineEdit(uri)
        self.layout.addWidget(self.uri_input)

        btn_row = QHBoxLayout()
        btn_save = QPushButton("Save")
        btn_cancel = QPushButton("Cancel")
        btn_delete = QPushButton("Delete")
        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_delete)
        self.layout.addLayout(btn_row)

        btn_save.clicked.connect(self.save)
        btn_cancel.clicked.connect(self._on_cancel)
        btn_delete.clicked.connect(self._on_delete)


    def save(self):
        new_hotkey = self.hotkey_input.text().strip()
        kind = self.kind_input.text().strip() or "slot"

        new_action = {"kind": kind}

        new_slots = self._settings.data["slots"]

        if kind == "slot":
            slot_id_text = self.slot_id_input.text().strip()
            if slot_id_text.isdigit():
                slot_id = int(slot_id_text)
                new_action["slot_id"] = slot_id

                uri = self.uri_input.text().strip()

                # make sure slot exists in settings
                if str(slot_id) not in new_slots:
                    new_slots[str(slot_id)] = {"type": "track", "uri": uri}
                else:
                    new_slots[str(slot_id)]["uri"] = uri

        # Update settings hotkeys: rename key if hotkey changes
        hotkeys = self._settings.data["hotkeys"]
        if self._old_hotkey in hotkeys:
            del hotkeys[self._old_hotkey]
        hotkeys[new_hotkey] = new_action

        self._settings.save()

        self._on_saved(self._binding, self._old_hotkey, new_hotkey, new_action, new_slots)
