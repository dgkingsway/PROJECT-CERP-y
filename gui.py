from PyQt6.QtWidgets import QPushButton, QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import speech

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
        result = speech.recognize_speech()
        self.label.setText(result)

if __name__ == "__main__":
    app = QApplication([])
    window = CERPApp()
    window.show()
    app.exec()
