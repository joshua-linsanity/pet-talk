import sys
import cv2
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

##############################
# Helper functions #
##############################

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

##############################
# Video Widget (OpenCV feed) #
##############################
class VideoWidget(QLabel):
    def __init__(self, parent=None):
        super(VideoWidget, self).__init__(parent)
        # Open the default camera (index 0)
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Cannot open camera")
            sys.exit(1)
        # Set up a timer to grab frames
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Approximately 30 FPS

        # Make sure the widget expands to fill vertical space
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Convert BGR (OpenCV) to RGB (Qt)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            # Scale the pixmap to match the widget's height (width may be larger)
            scaled_pix = QPixmap.fromImage(qimg).scaledToHeight(self.height(), Qt.SmoothTransformation)
            self.setPixmap(scaled_pix)

    def get_current_frame(self):
        ret, frame = self.cap.read()
        if ret: return frame
        return None
    
    def closeEvent(self, event):
        self.cap.release()
        event.accept()

#######################
# Chat UI Components  #
#######################
class ChatBubble(QLabel):
    def __init__(self, text, is_sender=True):
        super().__init__(text)
        self.setWordWrap(True)
        self.setMaximumWidth(400) # Limit bubble width
        
        # iMessage-style colors
        if is_sender:
            bg_color = "#007AFF"  # Blue for sender
            text_color = "#FFFFFF"
        else:
            bg_color = "#E5E5EA"  # Gray for receiver
            text_color = "#000000"
            
        style = f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: 15px;
                padding: 10px;
                font-size: 14px;
            }}
        """
        self.setStyleSheet(style)

class ChatWindow(QWidget):
    def __init__(self, video_widget):
        super().__init__()
        # Main layout for chat panel
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10,10,10,10)
        self.layout.setSpacing(10)
        self.video_widget = video_widget
        
        # Add header with contact info
        self.header = self._create_header()
        self.layout.addWidget(self.header)
        
        # Scroll area for chat messages
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        self.chat_content = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_content)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.chat_content)
        self.layout.addWidget(self.scroll_area)
        
        # Input field for messages
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("iMessage")
        # Pressing Enter sends the message
        self.input_field.returnPressed.connect(self.send_message)
        self.layout.addWidget(self.input_field)
    
    def _create_header(self):
        header_widget = QWidget(self)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        
        # Profile picture
        profile_pic = QLabel(self)
        pixmap = create_circular_pixmap("pfp.png", 50)
        if pixmap.isNull():
            # Use a placeholder if image not found
            pixmap = QPixmap(50, 50)
            pixmap.fill(Qt.gray)
        pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        profile_pic.setPixmap(pixmap)
        profile_pic.setFixedSize(50, 50)
        
        # Contact name
        name_label = QLabel("Hippo", self)
        name_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        name_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        
        header_layout.addWidget(profile_pic)
        header_layout.addWidget(name_label)
        header_layout.addStretch()  # Push content to the left
        
        return header_widget
    
    def send_message(self):
        text = self.input_field.text().strip()
        if text:
            # Create sender bubble (aligned to right)
            sender_layout = QHBoxLayout()
            sender_layout.addStretch()  # Push bubble to right
            bubble = ChatBubble(text, is_sender=True)
            sender_layout.addWidget(bubble)
            self.chat_layout.addLayout(sender_layout)
            
            self.input_field.clear()
            self._scroll_to_bottom()
            # Simulate a response message
            self.add_received_message()

    def process_with_vision_api(self, question):
        frame = self.video_widget.get_current_frame()
        while frame is None:
            frame = self.video_widget.get_current_frame()
        
        # TODO: query the current frame

    
    def add_received_message(self, text):
        # Create receiver bubble (aligned to left)
        receiver_layout = QHBoxLayout()
        bubble = ChatBubble(text, is_sender=False)
        receiver_layout.addWidget(bubble)
        receiver_layout.addStretch()  # Push bubble to left
        self.chat_layout.addLayout(receiver_layout)
        self._scroll_to_bottom()
    
    def _scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

#######################
# Main Combined Window#
#######################
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video & Chat")
        self.resize(900, 600)
        
        # Horizontal layout: Video feed on the left, Chat UI on the right
        layout = QHBoxLayout(self)
        self.video_widget = VideoWidget(self)
        # Allow video to expand more (especially in width) if needed
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.video_widget, 1) # stretch factor
        
        self.chat_window = ChatWindow(video_widget=self.video_widget)
        self.chat_window.setMinimumWidth(400)
        self.chat_window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.chat_window, 1)  # stretch factor

#######################
# Run the Application #
#######################
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
