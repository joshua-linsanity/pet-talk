import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QScrollArea
)
from PyQt5.QtCore import Qt

class ChatBubble(QLabel):
    def __init__(self, text, is_sender=True):
        super().__init__(text)
        self.setWordWrap(True)
        # Style bubble with rounded corners and padding
        style = """
            QLabel {{
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 8px;
                background-color: {};
                max-width: 300px;
            }}
        """.format("#DCF8C6" if is_sender else "#FFF")
        self.setStyleSheet(style)

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat Window")
        self.resize(400, 600)

        self.layout = QVBoxLayout(self)

        # Create a scroll area for the chat bubbles
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.addStretch()  # Push bubbles upward
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        # Input area
        self.input_layout = QHBoxLayout()
        self.text_input = QLineEdit()
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.input_layout.addWidget(self.text_input)
        self.input_layout.addWidget(self.send_button)
        self.layout.addLayout(self.input_layout)

    def send_message(self):
        text = self.text_input.text().strip()
        if text:
            # Create sender bubble (aligned to right)
            bubble = ChatBubble(text, is_sender=True)
            bubble_layout = QHBoxLayout()
            bubble_layout.addStretch()
            bubble_layout.addWidget(bubble)
            self.scroll_layout.insertLayout(self.scroll_layout.count()-1, bubble_layout)

            self.text_input.clear()

            # Optionally simulate a response message (aligned to left)
            self.add_response("Echo: " + text)

            # Scroll to the bottom
            self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().maximum()
            )

    def add_response(self, text):
        bubble = ChatBubble(text, is_sender=False)
        bubble_layout = QHBoxLayout()
        bubble_layout.addWidget(bubble)
        bubble_layout.addStretch()
        self.scroll_layout.insertLayout(self.scroll_layout.count()-1, bubble_layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())
