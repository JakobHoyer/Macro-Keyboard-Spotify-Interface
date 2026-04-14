from PySide6.QtWidgets import QPushButton, QSizePolicy
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QSize, QEvent

class PixelArtButton(QPushButton):
    def __init__(
        self, 
        normal_path: str,
        hover_path: str | None = None,
        pressed_path: str | None = None,
        parent=None, 
        padding: int = 6,
        integer_scale: bool = True,
    ):
        super().__init__(parent)
        self._pix_normal = QPixmap(normal_path)
        self._pix_hover = QPixmap(hover_path) if hover_path else QPixmap()
        self._pix_pressed = QPixmap(pressed_path) if pressed_path else QPixmap()
        self._padding = padding 
        self._integer_scale = integer_scale

        self._state = "normal" # normal / hover / pressed

        #self.setMinimumSize(self._base.width() + 2*padding, self._base.height() + 2*padding)
        self.setFlat(True) # no 3D effect
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setStyleSheet("""
            QPushButton { border: none; background: transparent; padding: 0px; }
        """)

        self.setMouseTracking(True) # this enables hover events

        self._update_icon()
    

    def enterEvent(self, event):
        super().enterEvent(event)
        if self.isEnabled() and self._state != "pressed":
            self._state = "hover"
            self._update_icon()


    def leaveEvent(self, event):
        super().leaveEvent(event)
        if self.isEnabled() and self._state != "pressed":
            self._state = "normal"
            self._update_icon()


    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self.isEnabled() and event.button() == Qt.LeftButton:
            self._state = "pressed"
            self._update_icon()


    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if not self.isEnabled():
            return

        # if the mouse is still over the button then do hover or normal.
        if self.rect().contains(event.position().toPoint()):
            self._state = "hover"
        else:
            self._state = "normal"
        self._update_icon()


    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.EnabledChange:
            # hvis den bliver disabled/enabled, så reset state
            self._state = "normal"
            self._update_icon()


    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_icon()


    def _current_pixmap(self) -> QPixmap:
        if self._state == "pressed" and not self._pix_pressed.isNull():
            return self._pix_pressed
        if self._state == "hover" and not self._pix_hover.isNull():
            return self._pix_hover
        return self._pix_normal


    def _update_icon(self):
        base = self._current_pixmap()
        if base.isNull():
            return

        w = max(1, self.width() - 2 * self._padding)
        h = max(1, self.height() - 2 * self._padding)
        target = min(w, h)

        bw, bh = base.width(), base.height()
        if bw <= 0 or bh <= 0:
            return

        if self._integer_scale:
            scale = min(target // bw, target // bh)
            if scale < 1:
                scale = 1
            new_size = QSize(bw * scale, bh * scale)
        else:
            new_size = QSize(target, target)

        pix = base.scaled(new_size, Qt.KeepAspectRatio, Qt.FastTransformation)

        self.setIcon(QIcon(pix))
        self.setIconSize(pix.size())