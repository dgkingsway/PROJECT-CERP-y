import sys
import logging
import argparse
from PyQt6.QtWidgets import (
    QPushButton, QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QTextEdit, QScrollArea
)
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from speech import SpeechProcessor
from automation import Automation
from logging.handlers import RotatingFileHandler
import os
import speech_recognition as sr

# Ensure the logs directory exists
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

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

class HelloListenerThread(QThread):
    """Thread to listen for the 'hello' wake word to trigger voice control."""
    hello_detected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.running = True

    def run(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.running:
                try:
                    logging.info("Listening for 'hello' wake word...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
                    command = self.recognizer.recognize_google(audio, language="en-US").lower()
                    if "hello" in command:
                        logging.info("Detected 'hello' wake word.")
                        self.hello_detected.emit()
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    logging.error(f"Speech recognition request failed: {e}")
                except Exception as e:
                    logging.error(f"Hello listener failed: {e}")

    def stop(self):
        self.running = False

class CERPApp(QMainWindow):
    """Main GUI for CERP Voice Automation with enhanced accessibility."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CERP - Voice & Automation")
        self.setGeometry(100, 100, 800, 600)

        self.auto = Automation()
        self.speech = SpeechProcessor()

        self.initUI()
        self.start_hello_listener()
        logging.info("CERP GUI initialized.")

    def initUI(self):
        """Initialize the UI components with accessibility features."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a scrollable area for the layout
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)

        self.label = QLabel("CERP Voice Automation", self)
        self.label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.status_label = QLabel("Status: Waiting for command... Say 'hello' to start voice control.", self)
        self.status_label.setFont(QFont("Arial", 16))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.history_text = QTextEdit(self)
        self.history_text.setFont(QFont("Arial", 14))
        self.history_text.setReadOnly(True)
        self.history_text.setFixedHeight(150)
        layout.addWidget(self.history_text)

        self.voice_btn = QPushButton("Use Voice Control", self)
        self.voice_btn.setStyleSheet("""
            QPushButton { background-color: #3498DB; color: white; font-size: 18px; padding: 15px; border-radius: 15px; }
            QPushButton:hover { background-color: #2980B9; }
        """)
        self.voice_btn.setToolTip("Press to start voice control (or say 'hello')")
        self.voice_btn.clicked.connect(self.run_speech_recognition)
        layout.addWidget(self.voice_btn)

        self.quit_btn = QPushButton("Quit", self)
        self.quit_btn.setStyleSheet("""
            QPushButton { background-color: #E74C3C; color: white; font-size: 18px; padding: 15px; border-radius: 15px; }
            QPushButton:hover { background-color: #C0392B; }
        """)
        self.quit_btn.setToolTip("Press to quit the application")
        self.quit_btn.clicked.connect(self.close)
        layout.addWidget(self.quit_btn)

        layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(scroll)

    def start_hello_listener(self):
        """Start the thread to listen for the 'hello' wake word."""
        self.hello_thread = HelloListenerThread()
        self.hello_thread.hello_detected.connect(self.run_speech_recognition)
        self.hello_thread.start()

    def run_speech_recognition(self):
        """Start speech recognition in a separate thread for general commands."""
        if hasattr(self, 'speech_thread') and self.speech_thread.isRunning():
            return
        self.voice_btn.setEnabled(False)
        self.voice_btn.setText("Listening...")
        self.status_label.setText("Status: Listening...")
        self.speech_thread = SpeechThread(self.speech)
        self.speech_thread.result_signal.connect(self.process_command)
        self.speech_thread.finished.connect(lambda: self.voice_btn.setEnabled(True))
        self.speech_thread.finished.connect(lambda: self.voice_btn.setText("Use Voice Control"))
        self.speech_thread.start()

    def process_command(self, command: str):
        """Process general commands from speech recognition."""
        if command.startswith("Error:") or command.lower().startswith("sorry"):
            self.label.setText(command)
            self.status_label.setText("Status: Error occurred.")
            self.history_text.append(f"> {command}\nResult: Error occurred\n")
        else:
            self.label.setText(f"Executing: {command}")
            result = self.auto.execute_task(command)
            if "exit" in command.lower():
                self.status_label.setText("Status: Exiting application...")
                self.history_text.append(f"> {command}\nResult: {result}\n")
                cursor = self.history_text.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.history_text.setTextCursor(cursor)
                QApplication.quit()
                return
            self.status_label.setText("Status: Command executed.")
            self.history_text.append(f"> {command}\nResult: {result}\n")
        cursor = self.history_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.history_text.setTextCursor(cursor)

    def closeEvent(self, event):
        """Handle application close event to stop the hello listener thread."""
        if hasattr(self, 'hello_thread'):
            self.hello_thread.stop()
            self.hello_thread.wait()
        event.accept()

if __name__ == "__main__":
    # Parse command-line arguments to start minimized
    parser = argparse.ArgumentParser(description="CERP Voice Automation")
    parser.add_argument('--minimized', action='store_true', help="Start the application minimized")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = CERPApp()
    if args.minimized:
        window.showMinimized()
    else:
        window.show()
    sys.exit(app.exec())