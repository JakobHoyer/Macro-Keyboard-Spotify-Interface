from PySide6.QtWidgets import QWidget, QComboBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton

from app.core.actions import ActionKind
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

        name_label = QLabel("Name:")
        name_label.setStyleSheet("color: white;")
        self.layout.addWidget(name_label)

        self.name_input = QLineEdit(self._model.name)
        self.layout.addWidget(self.name_input)

        hotkey_label = QLabel("Hotkey:")
        hotkey_label.setStyleSheet("color: white;")
        self.layout.addWidget(hotkey_label)

        self.hotkey_input = QLineEdit(self._model.hotkey)
        self.layout.addWidget(self.hotkey_input)

        action_label = QLabel("Action type:")
        action_label.setStyleSheet("color: white;")
        self.layout.addWidget(action_label)

        self.combobox = QComboBox()
        self.combobox.addItems([
            "Play/Pause",
            "Next song",
            "Previous song",
            "Play Spotify target",
        ])
        self.layout.addWidget(self.combobox)
        self._set_combobox_from_kind(self._model.kind)

        target_type_label = QLabel("Spotify target type:")
        target_type_label.setStyleSheet("color: white;")
        self.layout.addWidget(target_type_label)
        self.target_type_label = target_type_label

        self.target_type_box = QComboBox()
        self.target_type_box.addItems(["track", "playlist", "uris"])
        self.target_type_box.setCurrentText(self._model.target_type or "track")
        self.layout.addWidget(self.target_type_box)

        spotify_uri_label = QLabel("Spotify URI:")
        spotify_uri_label.setStyleSheet("color: white;")
        self.layout.addWidget(spotify_uri_label)
        self.spotify_uri_label = spotify_uri_label

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
        self.combobox.currentIndexChanged.connect(self._update_spotify_fields_enabled)

        self._update_spotify_fields_enabled()

    def _set_combobox_from_kind(self, kind: ActionKind):
        mapping = {
            ActionKind.PLAY_PAUSE: 0,
            ActionKind.NEXT: 1,
            ActionKind.PREV: 2,
            ActionKind.PLAY_SPOTIFY: 3,
        }
        self.combobox.setCurrentIndex(mapping.get(kind, 3))

    def _update_spotify_fields_enabled(self):
        is_spotify_binding = self.get_combobox_value() == ActionKind.PLAY_SPOTIFY
        self.target_type_label.setEnabled(is_spotify_binding)
        self.target_type_box.setEnabled(is_spotify_binding)
        self.spotify_uri_label.setEnabled(is_spotify_binding)
        self.uri_input.setEnabled(is_spotify_binding)

    def save(self):
        name = self.name_input.text().strip() or "Binding"
        hotkey = self.hotkey_input.text().strip()
        kind = self.get_combobox_value()

        target_type = ""
        uri = ""

        if kind == ActionKind.PLAY_SPOTIFY:
            target_type = self.target_type_box.currentText().strip()
            uri = self.uri_input.text().strip()

        new_model = BindingModel(
            id=self._model.id,
            name=name,
            hotkey=hotkey,
            kind=kind,
            target_type=target_type,
            uri=uri,
        )

        self._on_saved(self._binding, new_model)

    def get_combobox_value(self) -> ActionKind:
        translation_list = [
            ActionKind.PLAY_PAUSE,
            ActionKind.NEXT,
            ActionKind.PREV,
            ActionKind.PLAY_SPOTIFY,
        ]
        kind_id = self.combobox.currentIndex()
        return translation_list[kind_id]