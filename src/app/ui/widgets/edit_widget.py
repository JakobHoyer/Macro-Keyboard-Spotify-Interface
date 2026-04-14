from PySide6.QtWidgets import QWidget, QComboBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton

from app.core.binding_model import BindingModel
from app.ui.widgets.binding_widget import BindingWidget
from app.config.settings import Settings


class EditWidget(QWidget):
    def __init__(self, binding_widget: BindingWidget, settings: Settings, on_saved, on_cancel, on_delete):
        super().__init__()
        self._settings = settings
        self._binding = binding_widget
        self._model = binding_widget._model
        self._on_saved = on_saved
        self._on_cancel = on_cancel
        self._on_delete = on_delete

        self.layout = QVBoxLayout(self)

        self._old_hotkey = self._model.hotkey

        hotkey_label = QLabel("Hotkey:")
        hotkey_label.setStyleSheet("color: white;")
        self.layout.addWidget(hotkey_label)

        self.hotkey_input = QLineEdit(self._model.hotkey)
        self.layout.addWidget(self.hotkey_input)

        action_list = ["Play/Pause", "Next song", "Previous song", "Play playlist/song from link below"]
        action_label = QLabel("Action type:")
        action_label.setStyleSheet("color: white;")
        self.layout.addWidget(action_label)

        self.combobox = QComboBox()
        self.combobox.addItems(action_list)
        self.layout.addWidget(self.combobox)
        self._set_combobox_from_kind(self._model.kind)

        slot_id_label = QLabel("Slot id:")
        slot_id_label.setStyleSheet("color: white;")
        self.layout.addWidget(slot_id_label)

        self.slot_id_input = QLineEdit("" if self._model.slot_id is None else str(self._model.slot_id))
        self.layout.addWidget(self.slot_id_input)

        spotify_uri_label = QLabel("Spotify URI:")
        spotify_uri_label.setStyleSheet("color: white;")
        self.layout.addWidget(spotify_uri_label)

        self.uri_input = QLineEdit(self._model.uri)
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


    def _set_combobox_from_kind(self, kind: str):
        mapping = {
            "play_pause": 0,
            "next": 1,
            "prev": 2,
            "slot": 3,
        }
        self.combobox.setCurrentIndex(mapping.get(kind, 3))


    def save(self):
        new_hotkey = self.hotkey_input.text().strip()
        kind = self.get_combobox_value()

        slot_id = None
        slot_type = ""
        uri = ""

        if kind == "slot":
            slot_id_text = self.slot_id_input.text().strip()
            if slot_id_text.isdigit():
                slot_id = int(slot_id_text)
                uri = self.uri_input.text().strip()

                existing_slot = self._settings.data["slots"].get(str(slot_id), {})
                slot_type = existing_slot.get("type", "track")

        new_model = BindingModel(
            hotkey=new_hotkey,
            kind=kind,
            slot_id=slot_id,
            slot_type=slot_type,
            uri=uri,
        )

        self._on_saved(self._binding, self._old_hotkey, new_model)


    def get_combobox_value(self) -> str:
        translation_list = ["play_pause", "next", "prev", "slot"]
        kindid = self.combobox.currentIndex()
        value = translation_list[kindid].strip()
        return value