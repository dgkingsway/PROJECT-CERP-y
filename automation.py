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
        self.history: List[str] = []
        self.max_history = 10
        self.voice_typing_active = False
        self.recognizer = sr.Recognizer()
        logging.info("Automation module initialized.")

    def open_application(self, app_name: str) -> str:
        """Open an application by name (supports multi-word names joined with spaces)."""
        logging.info(f"Attempting to open application: {app_name}")
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

    def _add_to_history(self, action: str):
        """Add action to history, limiting to max_history entries."""
        self.history.append(action)
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_history(self) -> List[str]:
        """Return the command history."""
        return self.history.copy()
