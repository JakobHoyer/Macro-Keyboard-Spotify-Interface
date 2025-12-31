from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Signal, QUrl
from PySide6.QtGui import QPixmap
from PySide6.QtNetwork import (
    QNetworkAccessManager,
    QNetworkRequest,
    QNetworkDiskCache,
    QNetworkReply,
)

from platformdirs import user_cache_dir


class ImageLoader(QObject):
    loaded = Signal(str, QPixmap)   # (url, pixmap)
    failed = Signal(str, str)       # (url, error)

    def __init__(self, parent: Optional[QObject] = None, max_cache_mb: int = 100):
        super().__init__(parent)

        self.nam = QNetworkAccessManager(self)

        # Disk cache med max størrelse (evicter automatisk)
        cache_dir = Path(user_cache_dir("macro-spotify-app")) / "image_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        disk_cache = QNetworkDiskCache(self)
        disk_cache.setCacheDirectory(str(cache_dir))
        disk_cache.setMaximumCacheSize(max_cache_mb * 1024 * 1024)  # bytes

        self.nam.setCache(disk_cache)

    def load(self, url: str) -> None:
        qurl = QUrl(url)
        if not qurl.isValid() or qurl.scheme() not in ("http", "https"):
            self.failed.emit(url, "Invalid URL")
            return

        req = QNetworkRequest(qurl)

        # Workaround for "Unknown error" (ofte HTTP/2 på Linux/Qt)
        req.setAttribute(QNetworkRequest.Http2AllowedAttribute, False)

        # Qt6 redirect policy (Qt5 FollowRedirectsAttribute findes ikke her)
        req.setAttribute(QNetworkRequest.RedirectPolicyAttribute,
                        QNetworkRequest.NoLessSafeRedirectPolicy)

        req.setRawHeader(b"User-Agent", b"Mozilla/5.0")

        reply = self.nam.get(req)

        def on_error(e):
            print("Qt network error enum:", int(e), "->", reply.errorString())

        def on_finished():
            status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
            redir = reply.attribute(QNetworkRequest.RedirectionTargetAttribute)
            print("HTTP status:", status, "redir:", redir)

            if reply.error() != QNetworkReply.NoError:
                self.failed.emit(url, reply.errorString())
                reply.deleteLater()
                return

            data = reply.readAll()
            pix = QPixmap()
            if not pix.loadFromData(bytes(data)):
                self.failed.emit(url, "Could not decode image data")
            else:
                self.loaded.emit(url, pix)

            reply.deleteLater()

        reply.errorOccurred.connect(on_error)
        reply.finished.connect(on_finished)