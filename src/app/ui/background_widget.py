from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QPainter, QPixmap, QColor
from PySide6.QtCore import Qt, QTimer
from pathlib import Path

class BackgroundWidget(QWidget):
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        proj_dir = Path(__file__).parent.parent.parent # src
        total_path = Path(proj_dir / image_path).as_posix().replace("\\", "/")
        
        self._bg = QPixmap(total_path)

        # Layout til dine normale widgets ovenpå
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._bg.isNull():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        
        # "cover": fyld hele widgeten, crop hvis nødvendigt
        scaled = self._bg.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))
