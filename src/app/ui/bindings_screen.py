from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QPushButton
from PySide6.QtCore import Qt
from app.ui.widgets.binding_widget import BindingWidget

class BindingsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setMaximumWidth(400)
        self.layout = QVBoxLayout(self)
        self.scroll = QScrollArea()
        self.widget = QWidget()
        self.vbox = QVBoxLayout()

        create_button = QPushButton("Create New Binding")
        create_button.setFixedSize(150, 36)
        create_button.clicked.connect(lambda: self.create_binding_widget("New Binding", "New Action", "New Key"))
        self.layout.addWidget(create_button)
        self.layout.addWidget(self.scroll)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.widget.setLayout(self.vbox)

        for i in range(1,10):
            object = BindingWidget("Binding "+str(i), "Action "+str(i),"Key "+str(i))
            self.vbox.addWidget(object)
    
    def create_binding_widget(self, binding_name: str, action_assigned: str, key_assigned: str) -> None:
        binding_widget = BindingWidget(binding_name, action_assigned, key_assigned)
        self.vbox.insertWidget(0, binding_widget)