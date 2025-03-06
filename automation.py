import os
import webbrowser
import pyautogui
import keyboard
import subprocess
import psutil
import datetime
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL

# Function Definitions
def open_application(app_name):
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    }
    return subprocess.Popen(apps[app_name]) if app_name in apps else f"Application {app_name} not found."

def adjust_volume(level):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    volume.SetMasterVolumeLevelScalar(level / 100, None)
    return f"Volume set to {level}%."

def get_system_status():
    battery = psutil.sensors_battery()
    battery_percent = battery.percent if battery else "Unknown"
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    internet_status = "Connected" if psutil.net_if_stats().get('Wi-Fi', {}).isup else "Disconnected"
    return f"Battery: {battery_percent}%, Time: {current_time}, Internet: {internet_status}"

def window_management(action):
    actions = {
        "minimize": "win+down",
        "maximize": "win+up",
        "switch": "alt+tab",
    }
    keyboard.press_and_release(actions[action])
    return f"Performed {action}." if action in actions else f"Window action {action} not found."

def media_control(action):
    media_keys = {
        "play": "playpause",
        "pause": "playpause",
        "stop": "stop",
    }
    keyboard.press_and_release(media_keys[action])
    return f"Media {action}." if action in media_keys else f"Media control {action} not found."

# Function Mapping Dictionary
task_functions = {
    "open": open_application,
    "volume": adjust_volume,
    "system status": lambda _: get_system_status(),
    "window": window_management,
    "media": media_control,
}

# Function to Execute Tasks
def execute_task(task, value=None):
    return task_functions[task](value) if task in task_functions else "Invalid task."
