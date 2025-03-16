from PyQt6.QtWidgets import QPushButton, QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import speech

class SpeechThread(QThread):
    result_signal = pyqtSignal(str)  # Signal to update UI safely

    def run(self):
        result = speech.recognize_speech()
        self.result_signal.emit(result)  # Send result to main UI

class CERPApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CERP - Voice & Automation")
        self.setGeometry(100, 100, 600, 500)
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        self.label = QLabel("CERP Voice Automation", self)
        self.label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.voice_btn = QPushButton("Use Voice Control", self)
        self.voice_btn.setStyleSheet("background-color: #3498DB; color: white; font-size: 14px; padding: 10px; border-radius: 8px;")
        self.voice_btn.clicked.connect(self.run_speech_recognition)
        layout.addWidget(self.voice_btn)

        central_widget.setLayout(layout)

    def run_speech_recognition(self):
        self.voice_btn.setText("Listening...")  # Update button UI
        self.speech_thread = SpeechThread()  # Create thread
        self.speech_thread.result_signal.connect(self.update_label)  # Connect signal
        self.speech_thread.start()  # Run speech recognition in thread

    def update_label(self, result):
        self.voice_btn.setText("Use Voice Control")  # Reset button text
        self.label.setText(result)

if __name__ == "__main__":
    app = QApplication([])
    window = CERPApp()
    window.show()
    app.exec()
