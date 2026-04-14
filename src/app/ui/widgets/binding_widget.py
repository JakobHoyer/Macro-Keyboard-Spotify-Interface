from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton

from app.core.binding_model import BindingModel


class BindingWidget(QWidget):
    editRequested = Signal(object)    # emits self
    deleteRequested = Signal(object)  # emits self

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
        self._name_label.setText("Name:    Binding")
        self._action_label.setText(f"Action:    {self.provide_action_string()}")
        self._key_label.setText(f"Hotkey:     {self._model.hotkey}")


    def provide_action_string(self) -> str:
        if self._model.kind == "slot":
            if self._model.slot_id is None:
                return "slot (missing id)"
            if not self._model.uri:
                return f"slot {self._model.slot_id} (missing)"
            slot_type = self._model.slot_type or "unknown"
            return f"play {slot_type}"
        return self._model.kind


    def apply_changes(self, model: BindingModel):
        self._model = model
        self._refresh_labels()