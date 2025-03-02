import sys
import subprocess
import speech_recognition as sr
import pyttsx3
import difflib
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

# 🔹 Secure Text-to-Speech Engine
class VoiceAssistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

# 🔹 Automation Module (Flexible Commands)
class Automation:
    def __init__(self, assistant):
        self.assistant = assistant
        self.commands = {
            "notepad": self.open_notepad,
            "google": self.open_google,
            "calculator": self.open_calculator
        }
        self.variations = {
            "open notepad": "notepad",
            "launch notepad": "notepad",
            "start notepad": "notepad",
            "open google": "google",
            "launch google": "google",
            "go to google": "google",
            "search google": "google",
            "open calculator": "calculator",
            "launch calculator": "calculator"
        }

    def get_best_match(self, command):
        possible_commands = list(self.variations.keys())
        match = difflib.get_close_matches(command, possible_commands, n=1, cutoff=0.6)
        return self.variations.get(match[0], None) if match else None

    def execute_command(self, command):
        command_key = self.get_best_match(command)
        if command_key and command_key in self.commands:
            try:
                self.commands[command_key]()  # Call the function safely
            except Exception as e:
                self.assistant.speak("An error occurred while executing the command.")
                print(f"Error: {e}")
        else:
            self.assistant.speak("Sorry, I didn't understand. Try again.")

    def open_notepad(self):
        self.assistant.speak("Opening Notepad")
        try:
            subprocess.run(["notepad.exe"], check=True)
        except Exception as e:
            print(f"Error opening Notepad: {e}")

    def open_google(self):
        self.assistant.speak("Opening Google")
        try:
            subprocess.run(["cmd", "/c", "start https://www.google.com"], check=True)
        except Exception as e:
            print(f"Error opening Google: {e}")

    def open_calculator(self):
        self.assistant.speak("Opening Calculator")
        try:
            subprocess.run(["calc.exe"], check=True)
        except Exception as e:
            print(f"Error opening Calculator: {e}")

# 🔹 Improved Voice Recognition
class VoiceRecognition:
    def __init__(self, automation, assistant):
        self.recognizer = sr.Recognizer()
        self.automation = automation
        self.assistant = assistant

    def listen_for_command(self):
        with sr.Microphone() as source:
            self.assistant.speak("Listening for a command...")
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)  # Reduce background noise
            try:
                audio = self.recognizer.listen(source, timeout=8)  # Increased timeout
                command = self.recognizer.recognize_google(audio).lower()
                print(f"You said: {command}")
                self.assistant.speak(f"You said {command}")
                self.automation.execute_command(command)
            except sr.UnknownValueError:
                self.assistant.speak("Sorry, I couldn't understand. Please try again.")
            except sr.RequestError:
                self.assistant.speak("Could not connect to the speech service.")
            except Exception as e:
                print(f"Voice Recognition Error: {e}")

# 🔹 GUI Application
class CERPApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CERP - Secure PC Automation")
        self.setGeometry(100, 100, 400, 300)

        # Initialize modules
        self.assistant = VoiceAssistant()
        self.automation = Automation(self.assistant)
        self.voice_recognition = VoiceRecognition(self.automation, self.assistant)

        # UI Layout
        layout = QVBoxLayout()
        self.label = QLabel("Click a button or use voice commands")
        layout.addWidget(self.label)

        self.notepad_btn = QPushButton("Open Notepad")
        self.notepad_btn.clicked.connect(self.automation.open_notepad)
        layout.addWidget(self.notepad_btn)

        self.google_btn = QPushButton("Open Google")
        self.google_btn.clicked.connect(self.automation.open_google)
        layout.addWidget(self.google_btn)

        self.calculator_btn = QPushButton("Open Calculator")
        self.calculator_btn.clicked.connect(self.automation.open_calculator)
        layout.addWidget(self.calculator_btn)

        self.voice_btn = QPushButton("Use Voice Command")
        self.voice_btn.clicked.connect(self.voice_recognition.listen_for_command)
        layout.addWidget(self.voice_btn)

        self.setLayout(layout)

# 🔹 Run the Application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CERPApp()
    window.show()
    sys.exit(app.exec())
