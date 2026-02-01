from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton

class BindingWidget(QWidget):
    def __init__(self, binding_name: str = "Binding Name", action_assigned: str = "None", key_assigned: str = "None"):
        super().__init__()

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(6, 6, 6, 6)
        self.setFixedHeight(80)
        self.setMinimumWidth(200)
               
        binding_name = QLabel(binding_name)
        action_assigned = QLabel(f"{action_assigned}")
        key_assigned = QLabel(f"{key_assigned}")
        
        text_layout = QVBoxLayout()
        text_layout.addWidget(binding_name)
        text_layout.addWidget(action_assigned)
        text_layout.addWidget(key_assigned)
        self.layout.addLayout(text_layout)

        button_layout = QVBoxLayout()
        btn_edit = QPushButton("Edit")
        btn_delete = QPushButton("Delete")
        btn_edit.setFixedSize(52, 28)
        btn_delete.setFixedSize(52, 28)
        button_layout.addWidget(btn_edit)
        button_layout.addWidget(btn_delete)

        self.layout.addLayout(button_layout)

        btn_delete.clicked.connect(self.delete_self)


    def delete_self(self):
        self.setParent(None)
        self.deleteLater()
