##############################
# Round Out the Profile Pic  #
##############################
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import base64

def create_circular_pixmap(image_path, size):
    # Load the image
    pixmap = QPixmap(image_path)
    if pixmap.isNull():
        # Create a placeholder pixmap if loading fails
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.gray)

    # Crop the pixmap to a square based on the smallest dimension
    s = min(pixmap.width(), pixmap.height())
    rect = QRect((pixmap.width() - s) // 2, (pixmap.height() - s) // 2, s, s)
    pixmap = pixmap.copy(rect)

    # Create a square pixmap with transparency to hold the circular image
    circular = QPixmap(s, s)
    circular.fill(Qt.transparent)

    # Draw the circular image
    painter = QPainter(circular)
    painter.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addEllipse(0, 0, s, s)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, pixmap)
    painter.end()

    # Scale the resulting pixmap to the desired size
    return circular.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
