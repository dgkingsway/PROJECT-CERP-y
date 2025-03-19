import os
import webbrowser
import pyautogui
import keyboard
import subprocess
import psutil
import datetime
import logging
from typing import Dict, Tuple, Callable, List
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from logging.handlers import RotatingFileHandler
import speech_recognition as sr

# Configure logging with rotation
handler = RotatingFileHandler('logs/cerp.log', maxBytes=5 * 1024 * 1024, backupCount=2)
logging.basicConfig(
    handlers=[handler],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class Automation:
    """Class to handle computer automation tasks for CERP with history and feedback."""

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
        self.history = []
        self.max_history = 10
        self.voice_typing_active = False
        self.recognizer = sr.Recognizer()
        logging.info("Automation module initialized.")

    def open_application(self, app_name: str) -> str:
        """Open an application by name."""
        logging.info(f"Attempting to open application: {app_name}")
        try:
            normalized_app_name = app_name.lower().replace(" ", "")
            app_path = self.app_paths.get(normalized_app_name, None)
            if app_path:
                subprocess.Popen(app_path)
                message = f"Opening {app_name}..."
                self._add_to_history(message)
                logging.info(f"Successfully opened: {app_name}")
                return message
            logging.warning(f"Application not found: {app_name}")
            return f"Application {app_name} not found."
        except Exception as e:
            logging.error(f"Failed to open {app_name}: {e}")
            return f"Error opening {app_name}: {str(e)}"

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
        """Start voice typing in Notepad."""
        try:
            self.voice_typing_active = True
            self.open_application("notepad")
            pyautogui.sleep(1)  # Wait for Notepad to open
            pyautogui.hotkey('win', 'up')  # Maximize Notepad window
            message = "Voice typing started. Say 'stop voice typing' to stop."
            logging.info(message)
            self._add_to_history(message)

            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                while self.voice_typing_active:
                    logging.info("Listening for voice typing...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    try:
                        text = self.recognizer.recognize_google(audio, language="en-US")
                        pyautogui.write(text + " ")  # Type the recognized text into Notepad
                        logging.info(f"Typed: {text}")
                    except sr.UnknownValueError:
                        logging.warning("Could not understand audio.")
                    except sr.RequestError:
                        logging.error("Speech recognition request failed.")
                    except Exception as e:
                        logging.error(f"Voice typing failed: {e}")

            return "Voice typing stopped."
        except Exception as e:
            logging.error(f"Voice typing failed: {e}")
            return f"Error during voice typing: {str(e)}"

    def stop_voice_typing(self) -> str:
        """Stop voice typing."""
        self.voice_typing_active = False
        message = "Voice typing stopped."
        logging.info(message)
        self._add_to_history(message)
        return message

    def execute_task(self, command: str) -> str:
        """Execute a task based on the command."""
        logging.info(f"Executing command: {command}")
        try:
            parts = command.split(maxsplit=1)
            task = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if task == "open":
                if args:
                    return self.open_application(args)
                else:
                    return "Error: No application specified."
            elif task == "increase" and args == "volume":
                return self.adjust_volume(10.0)
            elif task == "decrease" and args == "volume":
                return self.adjust_volume(-10.0)
            elif task == "system" and args == "status":
                return self.get_system_status()
            elif task == "start" and args == "voice typing":
                return self.start_voice_typing()
            elif task == "stop" and args == "voice typing":
                return self.stop_voice_typing()
            else:
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