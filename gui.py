import sys
import logging
from PyQt6.QtWidgets import (
    QPushButton, QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QTextEdit
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from speech import SpeechProcessor
from automation import Automation
from logging.handlers import RotatingFileHandler

# Configure logging with rotation
handler = RotatingFileHandler('logs/cerp.log', maxBytes=5 * 1024 * 1024, backupCount=2)
logging.basicConfig(
    handlers=[handler],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class SpeechThread(QThread):
    """Thread for running speech recognition without freezing the UI."""
    result_signal = pyqtSignal(str)

    def __init__(self, speech_processor):
        super().__init__()
        self.speech = speech_processor

    def run(self):
        try:
            logging.info("Speech recognition thread started.")
            command = self.speech.listen()
            self.result_signal.emit(command if command else "Sorry, no command recognized.")
        except Exception as e:
            logging.error(f"Speech thread failed: {e}")
            self.result_signal.emit(f"Error: {str(e)}")


class CERPApp(QMainWindow):
    """Main GUI for CERP Voice Automation with enhanced accessibility."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CERP - Voice & Automation")
        self.setGeometry(100, 100, 800, 600)  # Increased window size for better layout

        self.auto = Automation()
        self.speech = SpeechProcessor()

        self.initUI()
        logging.info("CERP GUI initialized.")

    def initUI(self):
        """Initialize the UI components with accessibility features."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Title Label
        self.label = QLabel("CERP Voice Automation", self)
        self.label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        # Status Label
        self.status_label = QLabel("Status: Waiting for command...", self)
        self.status_label.setFont(QFont("Arial", 16))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # History Text Box
        self.history_text = QTextEdit(self)
        self.history_text.setFont(QFont("Arial", 14))
        self.history_text.setReadOnly(True)
        self.history_text.setFixedHeight(200)  # Increased height for better visibility
        layout.addWidget(self.history_text)

        # Voice Control Button
        self.voice_btn = QPushButton("Use Voice Control", self)
        self.voice_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                font-size: 18px;
                padding: 15px;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        self.voice_btn.setToolTip("Press to start voice control")
        self.voice_btn.clicked.connect(self.run_speech_recognition)
        layout.addWidget(self.voice_btn)

        # Voice Typing Button
        self.voice_typing_btn = QPushButton("Start Voice Typing", self)
        self.voice_typing_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: white;
                font-size: 18px;
                padding: 15px;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
        """)
        self.voice_typing_btn.setToolTip("Press to start voice typing")
        self.voice_typing_btn.clicked.connect(self.start_voice_typing)
        layout.addWidget(self.voice_typing_btn)

        # Quit Button
        self.quit_btn = QPushButton("Quit", self)
        self.quit_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                font-size: 18px;
                padding: 15px;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        self.quit_btn.setToolTip("Press to quit the application")
        self.quit_btn.clicked.connect(self.close)
        layout.addWidget(self.quit_btn)

        layout.addStretch()
        central_widget.setLayout(layout)

    def run_speech_recognition(self):
        """Start speech recognition in a separate thread."""
        if hasattr(self, 'speech_thread') and self.speech_thread.isRunning():
            return  # Prevent starting a new thread if one is already running
        self.voice_btn.setEnabled(False)
        self.voice_btn.setText("Listening...")
        self.status_label.setText("Status: Listening...")
        self.speech_thread = SpeechThread(self.speech)
        self.speech_thread.result_signal.connect(self.process_command)
        self.speech_thread.finished.connect(lambda: self.voice_btn.setEnabled(True))  # Re-enable button on thread finish
        self.speech_thread.start()

    def start_voice_typing(self):
        """Start voice typing."""
        self.voice_typing_btn.setEnabled(False)
        self.voice_typing_btn.setText("Listening...")
        self.status_label.setText("Status: Listening for voice typing...")
        result = self.auto.execute_task("start voice typing")
        self.status_label.setText(result)
        self.voice_typing_btn.setText("Start Voice Typing")
        self.voice_typing_btn.setEnabled(True)

    def process_command(self, command: str):
        """Process the command received from the speech recognition thread."""
        self.voice_btn.setEnabled(True)
        self.voice_btn.setText("Use Voice Control")

        if command.startswith("Error:"):
            self.label.setText(command)
            self.status_label.setText("Status: Error occurred.")
        elif command.lower().startswith("sorry"):
            self.label.setText(command)
            self.status_label.setText("Status: No command recognized.")
        else:
            self.label.setText(f"Executing: {command}")
            result = self.auto.execute_task(command)
            self.status_label.setText("Status: Command executed.")
            self.history_text.append(f"> {command}\nResult: {result}\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CERPApp()
    window.show()
    sys.exit(app.exec())