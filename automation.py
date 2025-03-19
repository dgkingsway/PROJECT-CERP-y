import os
import webbrowser
import pyautogui
import subprocess
import psutil
import datetime
import logging
from typing import Dict, List
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from logging.handlers import RotatingFileHandler
import speech_recognition as sr
import threading
import time

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

class Automation:
    """Class to handle computer automation tasks with history and feedback."""

    def __init__(self):
        pyautogui.FAILSAFE = True
        self.app_paths = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "word": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
            "excel": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
            "powerpoint": "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE"
        }
        self.web_apps = {
            "gmail": "https://mail.google.com",
            "youtube": "https://www.youtube.com",
            "instagram": "https://www.instagram.com",
            "google": "https://www.google.com"
        }
        self.processes = {}  # Track opened processes for closing
        self.history = []
        self.max_history = 10
        self.voice_typing_active = False
        self.recognizer = sr.Recognizer()
        logging.info("Automation module initialized.")

    def open_application(self, app_name: str) -> str:
        """Open an application or web app by name and track the process."""
        logging.info(f"Attempting to open: {app_name}")
        try:
            normalized_app_name = app_name.lower().replace(" ", "")
            if normalized_app_name in self.web_apps:
                # Open web app and track the browser process
                webbrowser.open(self.web_apps[normalized_app_name])
                time.sleep(1)  # Wait for the browser to open
                browser_process = None
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'].lower() in ["chrome.exe", "msedge.exe", "firefox.exe"]:
                        browser_process = proc
                        break
                if browser_process:
                    self.processes[normalized_app_name] = browser_process
                message = f"Opening {app_name} in browser..."
                self._add_to_history(message)
                logging.info(f"Successfully opened: {app_name}")
                return message
            app_path = self.app_paths.get(normalized_app_name)
            if app_path:
                process = subprocess.Popen(app_path)
                self.processes[normalized_app_name] = psutil.Process(process.pid)
                message = f"Opening {app_name}..."
                self._add_to_history(message)
                logging.info(f"Successfully opened: {app_name}")
                return message
            logging.warning(f"Application not found: {app_name}")
            return f"Application {app_name} not found."
        except Exception as e:
            logging.error(f"Failed to open {app_name}: {e}")
            return f"Error opening {app_name}: {str(e)}"

    def close_application(self, app_name: str) -> str:
        """Close a specific application or webpage."""
        logging.info(f"Attempting to close: {app_name}")
        try:
            normalized_app_name = app_name.lower().replace(" ", "")
            if normalized_app_name in self.processes:
                process = self.processes[normalized_app_name]
                if process.is_running():
                    process.terminate()
                    process.wait(timeout=5)  # Wait for the process to terminate
                del self.processes[normalized_app_name]
                message = f"Closed {app_name}."
                self._add_to_history(message)
                logging.info(f"Successfully closed: {app_name}")
                return message
            logging.warning(f"Application not tracked: {app_name}")
            return f"Application {app_name} not found in tracked processes."
        except Exception as e:
            logging.error(f"Failed to close {app_name}: {e}")
            return f"Error closing {app_name}: {str(e)}"

    def adjust_volume(self, change: float) -> str:
        """Adjust system volume by a percentage change."""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            current_volume = volume.GetMasterVolumeLevelScalar()
            new_volume = max(0.0, min(1.0, current_volume + (change / 100)))
            volume.SetMasterVolumeLevelScalar(new_volume, None)
            message = f"Volume adjusted to {int(new_volume * 100)}%."
            logging.info(message)
            self._add_to_history(message)
            return message
        except Exception as e:
            logging.error(f"Volume adjustment failed: {e}")
            return f"Error adjusting volume: {str(e)}"

    def get_system_status(self) -> str:
        """Return system status including battery, time, internet, CPU, and memory."""
        try:
            battery = psutil.sensors_battery()
            battery_status = f"{battery.percent}%" if battery else "Unknown"
            internet_status = "Connected" if any(iface.isup for iface in psutil.net_if_stats().values()) else "Disconnected"
            cpu_usage = f"{psutil.cpu_percent()}%"
            memory_usage = f"{psutil.virtual_memory().percent}%"
            status = (
                f"Battery: {battery_status}, Time: {datetime.datetime.now().strftime('%H:%M:%S')}, "
                f"Internet: {internet_status}, CPU: {cpu_usage}, Memory: {memory_usage}"
            )
            logging.info("System status retrieved")
            self._add_to_history(status)
            return status
        except Exception as e:
            logging.error(f"System status failed: {e}")
            return f"Error retrieving status: {str(e)}"

    def start_voice_typing(self) -> str:
        """Start voice typing in a separate thread."""
        if self.voice_typing_active:
            return "Voice typing is already active."
        self.voice_typing_active = True
        thread = threading.Thread(target=self._voice_typing_loop)
        thread.start()
        message = "Voice typing started. Say 'stop voice typing' to stop."
        logging.info(message)
        self._add_to_history(message)
        return message

    def _voice_typing_loop(self):
        """Voice typing loop running in a separate thread."""
        try:
            self.open_application("notepad")
            pyautogui.sleep(1)  # Wait for Notepad to open
            pyautogui.hotkey('win', 'up')  # Maximize Notepad window
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                while self.voice_typing_active:
                    logging.info("Listening for voice typing...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    try:
                        text = self.recognizer.recognize_google(audio, language="en-US")
                        if "stop voice typing" in text.lower():
                            self.stop_voice_typing()
                            break
                        pyautogui.write(text + " ")  # Type the recognized text
                        logging.info(f"Typed: {text}")
                    except sr.UnknownValueError:
                        logging.warning("Could not understand audio.")
                    except sr.RequestError:
                        logging.error("Speech recognition request failed.")
        except Exception as e:
            logging.error(f"Voice typing thread failed: {e}")
            self.voice_typing_active = False

    def stop_voice_typing(self) -> str:
        """Stop voice typing."""
        self.voice_typing_active = False
        message = "Voice typing stopped."
        logging.info(message)
        self._add_to_history(message)
        return message

    def skip_shorts(self) -> str:
        """Skip a YouTube Short by simulating a down arrow key press."""
        try:
            pyautogui.press("down")  # Simulates pressing the down arrow to skip a Short
            message = "Skipped a Short."
            logging.info(message)
            self._add_to_history(message)
            return message
        except Exception as e:
            logging.error(f"Failed to skip Short: {e}")
            return f"Error skipping Short: {str(e)}"

    def skip_next(self) -> str:
        """Skip to the next video or content (e.g., on YouTube or Instagram)."""
        try:
            # Ensure the browser window is in focus
            browser_names = ["chrome", "msedge", "firefox"]
            for proc in psutil.process_iter(['name']):
                if any(browser in proc.info['name'].lower() for browser in browser_names):
                    pyautogui.hotkey("alt", "tab")  # Switch to the browser
                    time.sleep(0.5)  # Wait for focus
                    break
            pyautogui.press("right")  # Simulates pressing the right arrow to skip to the next video
            time.sleep(0.5)  # Add a small delay to ensure the key press registers
            message = "Skipped to the next content."
            logging.info(message)
            self._add_to_history(message)
            return message
        except Exception as e:
            logging.error(f"Failed to skip to next content: {e}")
            return f"Error skipping to next content: {str(e)}"

    def exit_application(self) -> str:
        """Signal to exit the application."""
        message = "Exiting application..."
        logging.info(message)
        self._add_to_history(message)
        return message

    def execute_task(self, command: str) -> str:
        """Execute a task based on the command."""
        logging.info(f"Executing command: {command}")
        try:
            parts = command.split(maxsplit=2)
            task = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            task_mapping = {
                "open": lambda: self.open_application(args),
                "close": lambda: self.close_application(args),
                "increase volume": lambda: self.adjust_volume(10.0),
                "decrease volume": lambda: self.adjust_volume(-10.0),
                "system status": lambda: self.get_system_status(),
                "start voice typing": lambda: self.start_voice_typing(),
                "stop voice typing": lambda: self.stop_voice_typing(),
                "skip shorts": lambda: self.skip_shorts(),
                "skip next": lambda: self.skip_next(),
                "exit": lambda: self.exit_application(),
            }

            for key, func in task_mapping.items():
                if command.startswith(key):
                    return func()

            return "Invalid task."
        except Exception as e:
            logging.error(f"Command execution failed: {command}, Error: {e}")
            return f"Error executing command: {str(e)}"

    def _add_to_history(self, action: str):
        """Add action to history, limiting to max_history entries."""
        self.history.append(action)
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_history(self) -> List[str]:
        """Return the command history."""
        return self.history.copy()