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

# Configure logging with rotation
handler = RotatingFileHandler('logs/cerp.log', maxBytes=5*1024*1024, backupCount=2)
logging.basicConfig(
    handlers=[handler],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Automation:
    """Class to handle computer automation tasks for CERP with history and feedback."""
    
    def __init__(self):
        pyautogui.FAILSAFE = True
        self.app_paths: Dict[str, str] = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "word": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
            "excel": "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
            "powerpoint": "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE"
        }
        self.history: List[str] = []
        self.max_history = 10
        logging.info("Automation module initialized")

    def open_application(self, app_name: str) -> str:
        """Open an application by name (supports multi-word names joined with spaces)."""
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
        """Adjust system volume by a percentage change with feedback."""
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

    def clear_history(self):
        """Clear the command history."""
        self.history.clear()
        logging.info("Command history cleared")

    # Command mapping table
    TASKS: Dict[str, Tuple[Callable, Callable]] = {
        "open": (open_application, lambda self, args: (" ".join(args) if args else "",)),
        "volume": (adjust_volume, lambda self, args: (float(args[0]) if args and args[0].replace('.', '').isdigit() else 0.0,)),
        "system": (get_system_status, lambda self, args: ()),
        "window": (lambda self, action: keyboard.press_and_release({"minimize": "win+down", "maximize": "win+up", "switch": "alt+tab"}.get(action, "")), 
                   lambda self, args: (args[0] if args else "",)),
        "media": (lambda self, action: keyboard.press_and_release({"play": "playpause", "pause": "playpause", "stop": "stop"}.get(action, "")), 
                  lambda self, args: (args[0] if args else "",)),
        "search": (lambda self, query: webbrowser.open(f"https://www.google.com/search?q={query}"), 
                   lambda self, args: (" ".join(args) if args else "",)),
        "shortcut": (lambda self, action: keyboard.press_and_release({"copy": "ctrl+c", "paste": "ctrl+v"}.get(action, "")), 
                     lambda self, args: (args[0] if args else "",)),
        "mouse": (lambda self, x, y: pyautogui.moveTo(int(x), int(y), duration=0.5), 
                  lambda self, args: (int(args[0]) if len(args) > 0 and args[0].isdigit() else 0, int(args[1]) if len(args) > 1 and args[1].isdigit() else 0)),
        "click": (lambda self: pyautogui.click(), lambda self, args: ()),
        "increase": (adjust_volume, lambda self, args: (10.0,)),
        "decrease": (adjust_volume, lambda self, args: (-10.0,))
    }

    def execute_task(self, task: str, *args) -> str:
        """Execute a task based on the command using a mapping table."""
        logging.info(f"Executing task: {task}, Args: {args}")
        try:
            task_data = self.TASKS.get(task.lower(), (lambda self, *_: "Invalid task.", lambda self, _: ()))
            func, arg_processor = task_data
            processed_args = arg_processor(self, args)
            result = func(self, *processed_args)
            logging.info(f"Task executed: {task}, Args: {args}, Result: {result}")
            return result
        except Exception as e:
            logging.error(f"Task execution failed: {task}, Args: {args}, Error: {e}")
            return f"Error executing {task}: {str(e)}"

    def get_history(self) -> List[str]:
        """Return the command history."""
        return self.history.copy()