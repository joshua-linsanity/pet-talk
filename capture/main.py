import sys
import cv2
import PIL
import random
import base64
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from openai import OpenAI

worker = OpenAI()

##############################
# Worker Thread for Open AI  #
##############################

def get_load_message():
    messages = [
        "Hopping right into action, hold on a sec!",
        "Nibbling on some carrots of data, please wait!",
        "Hang tight, I'm leaping into your request!",
        "Carrots in hand, I’m busy crunching details!",
        "Hold your ears, I'm bounding over to it!",
        "Just a bunny hop away, almost there!",
        "Gathering carrots and cuddles, please wait!",
        "Ears up, I'm whisking up your request!",
        "In a hoppy hurry, your info is coming!",
        "Binkying through data, please hold on!",
        "Hopping into action, one carrot at a time!",
        "Pause for a moment, I'm on a bunny trail!",
        "Hare-ing on to the details, please wait!",
        "Bunny breath in, bunny breath out, almost ready!",
        "Tail wags and bunny hops, your info is near!",
        "Just a hop and a skip away from completion!",
        "Crunching carrots and data, hang tight!",
        "Hold tight, I'm just nibbling through the details!",
        "Hop, skip, and wait a bit longer, almost there!",
        "Bunny-speed loading in progress, hold your whiskers!"
    ]
    return random.choice(messages)

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

##############################
# Worker Thread for Open AI  #
##############################

class SweatshopWorker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, question, image_path, name, species):
        super().__init__()
        self.question = question
        self.image_path = image_path
        self.name = name
        self.species = species

    def run(self):
        try:
            base64_image = encode_image(self.image_path)
            prompt = (
                    "Determine if the following query is health-related or conversational. "
                    "Examples of health-related queries: 'Are you healthy?' or 'Are you okay?' etc. "
                    "If the query is health-related, reply HEALTH. Else, reply CONVO. "
                    "User query: "
                    )
            response = worker.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt + self.question,
                            },
                        ],
                    }
                ],
                max_tokens=300
            )
            response = response.choices[0].message.content
            if response == "HEALTH":
                health = True
            elif response == "CONVO": 
                health = False
            else: 
                print(response)
                raise RuntimeError("openai sucks too")

            if health: 
                prompt = (
                    f"You are a professional veterinarian specializing in dogs, cats, and bunnies. "
                    "Carefully *analyze the attached image* along with the user query and offer your clinical diagnosis. "
                    "(Note the user query may be addressed to the pet, but respond as a veterinarian. "
                    "If the pet appears healthy, respond as such. "
                    "Otherwise, report the health concerns that may be present in the pet. "
                    "Keep all responses under 1000 characters. "
                    "User query: "
                )
                response = worker.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt + self.question,
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                                },
                            ],
                        }
                    ],
                    max_tokens=300
                )
                response = response.choices[0].message.content

                prompt = ("Consider the following diagnosis by a veterinarian. "
                    f"You are named {self.name}. "
                    "Replace all third person references with first person references. "
                    "Make sure your tone is warm and cute! "
                    "**Make sure to preserve the medical/clinical information in the diagnosis.** "
                )
                response = worker.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt + response,
                                },
                            ],
                        }
                    ],
                    max_tokens=300
                )
                
                response = response.choices[0].message.content
                self.finished.emit(response)
            else:
                prompt = (
                    f"You are a {self.species} named {self.name}. Consider the image of yourself "
                    "attached. If the human's message asks about the meaning of a gesture that you are making, "
                    "you (as openai gpt) are to search the web for the interpretation of the action. "
                    "Respond to the human's message in a conversational, cute, but informative tone. "
                    "Message: "
                )
                response = worker.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt + self.question,
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                                },
                            ],
                        }
                    ],
                    max_tokens=300
                )

                response = response.choices[0].message.content
                self.finished.emit(response)
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

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            scaled_pix = QPixmap.fromImage(qimg).scaledToHeight(self.height(), Qt.SmoothTransformation)
            self.setPixmap(scaled_pix)

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
        self.setMaximumWidth(300)
        #if not is_sender: 
        #    self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        if is_sender:
            # bg_color = "#007AFF"
            bg_color = "#FAB8D8"
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
        self.setWordWrap(True)

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
        # Get the current frame and save it
        frame = self.video_widget.get_current_frame()
        while frame is None:
            frame = self.video_widget.get_current_frame()
        filename = "current_frame.jpg"
        if not cv2.imwrite(filename, frame):
            self.add_received_message("That image didn't process! Could you try again?")
            return

        # Display a loading indicator in the chat window
        self.show_loading_indicator()

        # Set up the worker and thread
        self.thread = QThread()
        self.worker = SweatshopWorker(question, filename, self.name, self.species)
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
        self.loading_label = ChatBubble(get_load_message(), is_sender=False)
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
        self.chat_layout.update()
        # bubble.adjustSize()
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
        name = "Hippo"
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
