from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton

class BindingWidget(QWidget):
    editRequested = Signal(object)    # emits self
    deleteRequested = Signal(object)  # emits self

    def __init__(self, hotkey: str, action: dict, slots: dict):
        super().__init__()
        self._hotkey = hotkey
        self._action = action
        self._slots = slots

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
        kind = self._action.get("kind", "")
        action_str = self.provide_action_string()
        self._name_label.setText("Name:    Binding")
        self._action_label.setText(f"Action:    {action_str}")
        self._key_label.setText(f"Hotkey:     {self._hotkey}")

    def provide_action_string(self) -> str:
        if self._action.get("kind") == "slot":
            slot_id = self._action.get("slot_id")
            if slot_id is None:
                return "slot (missing id)"
            slot = self._slots.get(str(slot_id))
            if not slot:
                return f"slot {slot_id} (missing)"
            return f"play {slot.get('type', 'unknown')}"
        return self._action.get("kind", "")

    # bruges når editoren har gemt ændringer:
    def apply_changes(self, hotkey: str, action: dict, slots: dict):
        self._hotkey = hotkey
        self._action = action
        self._slots = slots
        self._refresh_labels()
