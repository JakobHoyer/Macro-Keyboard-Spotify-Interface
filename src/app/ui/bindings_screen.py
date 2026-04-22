from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QPushButton
from PySide6.QtCore import Signal

from app.ui.widgets.binding_widget import BindingWidget
from app.ui.widgets.edit_widget import EditWidget
from app.config.settings import Settings
from app.core.binding_model import BindingModel


class BindingsScreen(QWidget):
    bindingsChanged = Signal()

    def __init__(self, settings: Settings):
        super().__init__()
        self._settings = settings

        self.layout = QHBoxLayout(self)

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

        self.editor_layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addLayout(self.editor_layout)

        self._current_editor = None
        self._current_binding = None

        self.populate_scroll_window()

    def populate_scroll_window(self):
        self._clear_binding_list()

        for model in self._settings.get_bindings():
            w = BindingWidget(model)
            w.editRequested.connect(self.open_editor_for)
            w.deleteRequested.connect(self.delete_binding)
            self.vbox.addWidget(w)

    def create_new_binding(self):
        model = BindingModel.new_user()
        w = BindingWidget(model)
        w.editRequested.connect(self.open_editor_for)
        w.deleteRequested.connect(self.delete_binding)
        self.vbox.insertWidget(0, w)
        self.open_editor_for(w)

    def _clear_binding_list(self):
        while self.vbox.count():
            item = self.vbox.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

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

    def on_binding_saved(self, binding_widget: BindingWidget, new_model: BindingModel):
        bindings = self._settings.get_bindings()

        updated_bindings = []
        replaced = False

        for binding in bindings:
            if binding.id == new_model.id:
                updated_bindings.append(new_model)
                replaced = True
                continue

            if new_model.hotkey and binding.hotkey == new_model.hotkey and binding.id != new_model.id:
                continue

            updated_bindings.append(binding)

        if not replaced:
            updated_bindings.append(new_model)

        self._settings.set_bindings(updated_bindings)
        self._settings.save()

        self.populate_scroll_window()
        self.bindingsChanged.emit()
        self._clear_editor()

    def delete_binding(self, binding_widget):
        binding_id = binding_widget._model.id

        bindings = [
            binding
            for binding in self._settings.get_bindings()
            if binding.id != binding_id
        ]

        self._settings.set_bindings(bindings)
        self._settings.save()

        self.populate_scroll_window()
        self.bindingsChanged.emit()
        self._clear_editor()