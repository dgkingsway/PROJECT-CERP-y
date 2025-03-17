import sys
import logging
from PyQt6.QtWidgets import QPushButton, QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QTextEdit
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from speech import SpeechProcessor
from automation import Automation
from logging.handlers import RotatingFileHandler

# Configure logging with rotation
handler = RotatingFileHandler('logs/cerp.log', maxBytes=5*1024*1024, backupCount=2)
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
            print("Thread started")  # Debug print
            command = self.speech.listen()
            self.result_signal.emit(command if command else "Sorry, no command recognized.")
        except Exception as e:
            logging.error(f"Speech thread failed: {e}")
            self.result_signal.emit(f"Error: {str(e)}")

class CERPApp(QMainWindow):
    """Main GUI for CERP Voice Automation with enhanced accessibility."""
    
    # Command state mapping
    COMMAND_STATES = {
        "error": lambda self, cmd: (self.label.setText(cmd), self.status_label.setText("Status: Waiting for command...")),
        "sorry": lambda self, cmd: (self.label.setText(cmd), self.status_label.setText("Status: Waiting for command...")),
        "default": lambda self, cmd: self._process_valid_command(cmd)
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CERP - Voice & Automation")
        self.setGeometry(100, 100, 600, 600)
        
        self.auto = Automation()
        self.speech = SpeechProcessor()
        
        self.initUI()
        logging.info("CERP GUI initialized")

    def initUI(self):
        """Initialize the UI components with accessibility features."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        self.label = QLabel("CERP Voice Automation", self)
        self.label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.status_label = QLabel("Status: Waiting for command...", self)
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
            background-color: #3498DB; 
            color: white; 
            font-size: 18px; 
            padding: 15px; 
            border-radius: 10px;
        """)
        self.voice_btn.setToolTip("Press to start voice control")
        self.voice_btn.clicked.connect(self.run_speech_recognition)
        layout.addWidget(self.voice_btn)

        self.quit_btn = QPushButton("Quit", self)
        self.quit_btn.setStyleSheet("""
            background-color: #E74C3C; 
            color: white; 
            font-size: 18px; 
            padding: 15px; 
            border-radius: 10px;
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

    def _process_valid_command(self, command: str):
        """Helper to process valid commands and update history."""
        logging.info(f"Received command in GUI: {command}")
        try:
            words = command.split()
            task = words[0].lower() if words else ""
            args = words[1:] if len(words) > 1 else []
            result = self.auto.execute_task(task, *args)
            self.label.setText(result)
            self.status_label.setText("Status: Command executed")
            self._update_history(result)
            logging.info(f"Command processed: {command}, Result: {result}")
        except Exception as e:
            self.label.setText(f"Error: {str(e)}")
            self.status_label.setText("Status: Waiting for command...")
            logging.error(f"Error processing command: {e}")
            self._update_history(f"Error: {str(e)}")

    def _update_history(self, text: str):
        """Update the history text box with the latest command result."""
        self.history_text.append(f"> {text}\n")

    def process_command(self, command: str):
        """Process the command received from the speech recognition thread."""
        self.voice_btn.setEnabled(True)
        self.voice_btn.setText("Use Voice Control")
        
        # Check if the command is an error or a default command
        if command.startswith("Error:"):
            self.COMMAND_STATES["error"](self, command)
        elif command.lower().startswith("sorry"):
            self.COMMAND_STATES["sorry"](self, command)
        else:
            self.COMMAND_STATES["default"](self, command)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CERPApp()
    window.show()
    sys.exit(app.exec())