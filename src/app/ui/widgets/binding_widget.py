from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton


class BindingWidget(QWidget):
    def __init__(self, hotkey: str, action: dict, slots: dict):
        super().__init__()
        self._hotkey = hotkey
        self._action = action
        self._slots = slots
        self._name = "Binding"
        self._action_kind = self._action["kind"]
        self._uri = ""

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(6, 6, 6, 6)
        self.setFixedHeight(80)
        self.setMinimumWidth(200)

        _action_string = self.provide_action_string()

        binding_name = QLabel(f"Name:    {self._name}")
        action_assigned = QLabel(f"Action:    {_action_string}")
        key_assigned = QLabel(f"Hotkey:     {self._hotkey}")
        
        text_layout = QVBoxLayout()
        text_layout.addWidget(binding_name)
        text_layout.addWidget(action_assigned)
        text_layout.addWidget(key_assigned)
        self.layout.addLayout(text_layout
        )

        button_layout = QVBoxLayout()
        btn_edit = QPushButton("Edit")
        btn_delete = QPushButton("Delete")
        btn_edit.setFixedSize(52, 28)
        btn_delete.setFixedSize(52, 28)
        button_layout.addWidget(btn_edit)
        button_layout.addWidget(btn_delete)

        self.layout.addLayout(button_layout)

        btn_delete.clicked.connect(self.delete_self)


    def provide_action_string(self) -> str:
        if (self._action_kind == "slot"):
            _id = self._action["slot_id"]
            return "play " + self._slots[str(_id)]["type"]
        else:
            return self._action_kind
        


    def delete_self(self):
        self.setParent(None)
        self.deleteLater()
        # remove from json file.
