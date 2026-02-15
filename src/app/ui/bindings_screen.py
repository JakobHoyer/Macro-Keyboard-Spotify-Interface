from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QPushButton

from app.ui.widgets.binding_widget import BindingWidget
from app.ui.widgets.edit_widget import EditWidget
from app.config.settings import Settings

class BindingsScreen(QWidget):
    def __init__(self, settings: Settings):
        super().__init__()
        self._settings = settings

        self.layout = QHBoxLayout(self)

        # venstre: binding liste
        self.binding_layout = QVBoxLayout()
        self.scroll = QScrollArea()
        self.scroll.setMaximumWidth(400)

        self.list_container = QWidget()
        self.vbox = QVBoxLayout(self.list_container)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.list_container)

        create_button = QPushButton("Create New Binding")
        create_button.setFixedSize(150, 36)
        create_button.clicked.connect(self.create_new_binding)

        self.binding_layout.addWidget(create_button)
        self.binding_layout.addWidget(self.scroll)
        self.layout.addLayout(self.binding_layout)

        # højre: editor (én ad gangen)
        self.editor_layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addLayout(self.editor_layout)

        self._current_editor = None
        self._current_binding = None

        self.populate_scroll_window()


    def populate_scroll_window(self):
        slots = self._settings.data["slots"]
        for hotkey, action in self._settings.data["hotkeys"].items():
            w = BindingWidget(hotkey=hotkey, action=action, slots=slots)
            w.editRequested.connect(self.open_editor_for)
            w.deleteRequested.connect(self.delete_binding)
            self.vbox.addWidget(w)


    def create_new_binding(self):
        # lav en tom/ny binding i UI
        slots = self._settings.data["slots"]
        w = BindingWidget("New Hotkey", {"kind": "slot", "slot_id": 1}, slots)
        w.editRequested.connect(self.open_editor_for)
        w.deleteRequested.connect(self.delete_binding)
        self.vbox.insertWidget(0, w)
        self.open_editor_for(w)

    def _clear_editor(self):
        if self._current_editor:
            self._current_editor.setParent(None)
            self._current_editor.deleteLater()
            self._current_editor = None


    def open_editor_for(self, binding_widget: BindingWidget):
        self._current_binding = binding_widget
        self._clear_editor()

        self._current_editor = EditWidget(
            binding_widget=binding_widget,
            settings=self._settings,
            on_saved=self.on_binding_saved,
            on_cancel=self._clear_editor,
            on_delete=lambda: self.delete_binding(binding_widget),
        )
        self.editor_layout.addWidget(self._current_editor)


    def on_binding_saved(self, binding_widget, old_hotkey, new_hotkey, new_action, new_slots):
        # opdater UI
        binding_widget.apply_changes(new_hotkey, new_action, new_slots)
        self._clear_editor()


    def delete_binding(self, binding_widget: BindingWidget):
        # TODO: fjern fra settings + save
        binding_widget.setParent(None)
        binding_widget.deleteLater()
        self._clear_editor()
