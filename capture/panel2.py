import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QLabel, QScrollArea
)
from PyQt5.QtCore import Qt

class ChatBubble(QLabel):
    def __init__(self, text, is_sender=True):
        super().__init__(text)
        self.setWordWrap(True)
        self.setMaximumWidth(250)  # Limit the bubble width
        # iMessage-style colors
        if is_sender:
            bg_color = "#007AFF"  # Blue for sender
            text_color = "#FFFFFF"
        else:
            bg_color = "#E5E5EA"  # Gray for receiver
            text_color = "#000000"
        # Styling: round corners, padding, and colors
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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iMessage Chat")
        self.resize(400, 600)
        
        # Main vertical layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        # Scroll area for chat bubbles
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        
        # Container widget and layout for chat bubbles
        self.chat_content = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_content)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.chat_content)
        
        self.layout.addWidget(self.scroll_area)
        
        # Input area
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("iMessage")
        # Connect the Enter key (returnPressed) to sending a message
        self.input_field.returnPressed.connect(self.send_message)
        self.layout.addWidget(self.input_field)
    
    def send_message(self):
        text = self.input_field.text().strip()
        if text:
            # Create and add sender bubble (aligned to right)
            sender_layout = QHBoxLayout()
            sender_layout.addStretch()  # Pushes the bubble to the right
            bubble = ChatBubble(text, is_sender=True)
            sender_layout.addWidget(bubble)
            self.chat_layout.addLayout(sender_layout)
            
            self.input_field.clear()
            self._scroll_to_bottom()
            
            # Simulate a response for demonstration purposes
            self.add_received_message("Echo: " + text)
    
    def add_received_message(self, text):
        # Create and add receiver bubble (aligned to left)
        receiver_layout = QHBoxLayout()
        bubble = ChatBubble(text, is_sender=False)
        receiver_layout.addWidget(bubble)
        receiver_layout.addStretch()  # Pushes the bubble to the left
        self.chat_layout.addLayout(receiver_layout)
        self._scroll_to_bottom()
    
    def _scroll_to_bottom(self):
        # Scroll to the bottom after adding a new message
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())
