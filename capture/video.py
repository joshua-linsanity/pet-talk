import sys
import cv2
import PIL
import time
from collections import deque
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from helpers import *
from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyARoDWGfPnfxYkzyMhU5I3ULLluH7o6qaM")

##############################
# Worker Thread for Gemini   #
##############################
class GeminiWorker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, question, video_path, name, species):
        super().__init__()
        self.question = question
        self.video_path = video_path
        self.name = name
        self.species = species

    def run(self):
        try:
            # Determine if the user query is conversational or medical
            message = (
                "Determine if the following query is health-related or conversational. "
                "Examples of health-related queries: 'Are you healthy?' or 'Are you okay?' etc. "
                "If the query is health-related, reply HEALTH. Else, reply CONVO. "
                "User query: "
            )
            code = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=message + self.question
            )
            health = (code.text.strip() == "HEALTH")

            # This is the long-running Gemini call using the video file
            video_file = client.files.upload(path=self.video_path)
            while videO_file.state.name == "PROCESSING":
                time.sleep(1)
                video_file = client.files.get(name=video_file.name)
            if video_file.state.name == "FAILED":
                raise ValueError(video_file.state.name)

            if health: 
                prompt = (
                    f"You are a professional veterinarian specializing in dogs, cats, and bunnies. "
                    "Carefully *analyze the attached video* along with the user query and offer your clinical diagnosis. "
                    "(Note the user query may be addressed to the pet, but respond as a veterinarian. "
                    "If the pet appears healthy, respond as such. "
                    "Otherwise, report the health concerns that may be present in the pet. "
                    "Keep all responses under 1000 characters. "
                    "User query: "
                )
                diagnosis = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[video_file, prompt]
                )

                message = ("Consider the following diagnosis by a veterinarian. "
                    f"You are named {self.name}. "
                    "Replace all third person references with first person references. "
                    "Make sure your tone is warm and friendly. "
                    "**Make sure to preserve the medical/clinical information in the diagnosis.** "
                )
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=message + diagnosis.text
                )
                self.finished.emit(response.text)
            else:
                prompt = (
                    f"You are a {self.species} named {self.name}. Consider the video of yourself "
                    "attached. Respond to the human's message in a conversational and cute tone. "
                    "Message: "
                )
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[video_file, prompt + self.question]
                )
                self.finished.emit(response.text)

        except Exception as e:
            self.error.emit(str(e))

##############################
# Video Widget (OpenCV feed) #
##############################
class VideoWidget(QLabel):
    def __init__(self, parent=None):
        super(VideoWidget, self).__init__(parent)
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Cannot open camera")
            sys.exit(1)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Buffer to store (timestamp, frame) tuples for the past 5 seconds
        self.frame_buffer = deque()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            now = time.time()
            # Store a copy of the original BGR frame in the buffer
            self.frame_buffer.append((now, frame.copy()))
            # Remove frames older than 5 seconds
            while self.frame_buffer and (now - self.frame_buffer[0][0] > 5):
                self.frame_buffer.popleft()
            # Convert frame to RGB for display
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            scaled_pix = QPixmap.fromImage(qimg).scaledToHeight(self.height(), Qt.SmoothTransformation)
            self.setPixmap(scaled_pix)

    def get_recent_video_clip(self, filename="recent_clip.mp4"):
        if not self.frame_buffer:
            return None
        # Get frame size from the first buffered frame
        first_frame = self.frame_buffer[0][1]
        height, width, channels = first_frame.shape
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        if fps == 0 or fps is None:
            fps = 30
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
        for ts, frame in self.frame_buffer:
            out.write(frame)
        out.release()
        return filename

    def get_current_frame(self):
        ret, frame = self.cap.read()
        return frame if ret else None
    
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
        self.setMaximumWidth(400)
        if is_sender:
            bg_color = "#007AFF"
            text_color = "#FFFFFF"
        else:
            bg_color = "#E5E5EA"
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
        self.adjustSize()

class ChatWindow(QWidget):
    def __init__(self, video_widget, name, species):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10,10,10,10)
        self.layout.setSpacing(10)
        self.video_widget = video_widget
        
        self.header = self._create_header()
        self.layout.addWidget(self.header)
        
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        self.chat_content = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_content)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.chat_content)
        self.layout.addWidget(self.scroll_area)
        
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("iMessage")
        self.input_field.returnPressed.connect(self.send_message)
        self.layout.addWidget(self.input_field)

        # Keep a reference to the loading widget so we can remove it later
        self.loading_label = None

        # Pet info
        self.name = name
        self.species = species

    def _create_header(self):
        header_widget = QWidget(self)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        
        profile_pic = QLabel(self)
        pixmap = create_circular_pixmap("pfp.png", 50)
        if pixmap.isNull():
            pixmap = QPixmap(50, 50)
            pixmap.fill(Qt.gray)
        pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        profile_pic.setPixmap(pixmap)
        profile_pic.setFixedSize(50, 50)
        
        name_label = QLabel("Hippo", self)
        name_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        name_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        
        header_layout.addWidget(profile_pic)
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        
        return header_widget
    
    def send_message(self):
        text = self.input_field.text().strip()
        if text:
            sender_layout = QHBoxLayout()
            sender_layout.addStretch()
            bubble = ChatBubble(text, is_sender=True)
            sender_layout.addWidget(bubble)
            self.chat_layout.addLayout(sender_layout)
            self.input_field.clear()
            self._scroll_to_bottom()
            self.process_query(text)

    def process_query(self, question):
        # Save the past 5 seconds of video feed to an MP4 file
        filename = self.video_widget.get_recent_video_clip()
        if not filename:
            self.add_received_message("No video available for the past 5 seconds. Please try again.")
            return

        # Display a loading indicator in the chat window
        self.show_loading_indicator()

        # Set up the worker and thread
        self.thread = QThread()
        self.worker = GeminiWorker(question, filename, self.name, self.species)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.error.connect(self.on_worker_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def show_loading_indicator(self):
        # Create a temporary loading bubble (aligned left)
        self.loading_label = ChatBubble("Paws a second! I'm hopping to it...", is_sender=False)
        loading_layout = QHBoxLayout()
        loading_layout.addWidget(self.loading_label)
        loading_layout.addStretch()
        self.chat_layout.addLayout(loading_layout)
        self._scroll_to_bottom()

    def remove_loading_indicator(self):
        # Remove the loading indicator widget from the layout
        if self.loading_label:
            # Assuming the loading label is inside a layout, remove it.
            for i in reversed(range(self.chat_layout.count())):
                item = self.chat_layout.itemAt(i)
                if item.layout() is not None:
                    layout = item.layout()
                    for j in range(layout.count()):
                        widget = layout.itemAt(j).widget()
                        if widget == self.loading_label:
                            # Remove the widget and its layout
                            widget.setParent(None)
                            self.chat_layout.removeItem(layout)
                            break
            self.loading_label = None

    def on_worker_finished(self, response_text):
        self.remove_loading_indicator()
        self.add_received_message(response_text)

    def on_worker_error(self, error_message):
        self.remove_loading_indicator()
        self.add_received_message("Error: " + error_message)

    def add_received_message(self, text):
        receiver_layout = QHBoxLayout()
        bubble = ChatBubble(text, is_sender=False)
        receiver_layout.addWidget(bubble)
        receiver_layout.addStretch()
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
        name = "Bambi"
        species = "Bunny"

        self.setWindowTitle("Video & Chat")
        self.resize(900, 600)
        
        layout = QHBoxLayout(self)
        self.video_widget = VideoWidget(self)
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.video_widget, 1)
        
        self.chat_window = ChatWindow(video_widget=self.video_widget, name=name, species=species)
        self.chat_window.setMinimumWidth(400)
        self.chat_window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.chat_window, 1)

#######################
# Run the Application #
#######################
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
