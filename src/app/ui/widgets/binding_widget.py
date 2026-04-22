from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton

from app.core.actions import ActionKind
from app.core.binding_model import BindingModel


class BindingWidget(QWidget):
    editRequested = Signal(object)
    deleteRequested = Signal(object)

    def __init__(self, model: BindingModel):
        super().__init__()
        self._model = model

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(6, 6, 6, 6)
        self.setFixedHeight(80)
        self.setMinimumWidth(200)

        self._name_label = QLabel()
        self._action_label = QLabel()
        self._key_label = QLabel()
        self._refresh_labels()

        text_layout = QVBoxLayout()
        text_layout.addWidget(self._name_label)
        text_layout.addWidget(self._action_label)
        text_layout.addWidget(self._key_label)
        self.layout.addLayout(text_layout)

        button_layout = QVBoxLayout()
        btn_edit = QPushButton("Edit")
        btn_delete = QPushButton("Delete")
        btn_edit.setFixedSize(52, 28)
        btn_delete.setFixedSize(52, 28)
        button_layout.addWidget(btn_edit)
        button_layout.addWidget(btn_delete)
        self.layout.addLayout(button_layout)

        btn_edit.clicked.connect(lambda: self.editRequested.emit(self))
        btn_delete.clicked.connect(lambda: self.deleteRequested.emit(self))

    def _refresh_labels(self):
        self._name_label.setText(f"Name:    {self._model.name or 'Binding'}")
        self._action_label.setText(f"Action:  {self.provide_action_string()}")
        self._key_label.setText(f"Hotkey:  {self._model.hotkey or '(none)'}")

    def provide_action_string(self) -> str:
        if self._model.kind == ActionKind.PLAY_SPOTIFY:
            if not self._model.uri:
                return "play Spotify target (missing URI)"
            return f"play {self._model.target_type or 'unknown'}"

        if self._model.kind == ActionKind.PLAY_PAUSE:
            return "play / pause"
        if self._model.kind == ActionKind.NEXT:
            return "next song"
        if self._model.kind == ActionKind.PREV:
            return "previous song"

        return self._model.kind.value

    def apply_changes(self, model: BindingModel):
        self._model = model
        self._refresh_labels()