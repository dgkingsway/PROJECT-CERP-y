import os
import webbrowser
import pyautogui
import keyboard
import subprocess
import psutil
import datetime
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL

def open_application(app_name):
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    }
    if app_name in apps:
        subprocess.Popen(apps[app_name])
        return f"Opening {app_name}..."
    return f"Application {app_name} not found."

def adjust_volume(level):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        volume.SetMasterVolumeLevelScalar(level / 100, None)
        return f"Volume set to {level}%."
    except Exception as e:
        return f"Error adjusting volume: {str(e)}"

def get_system_status():
    battery = psutil.sensors_battery()
    return f"Battery: {battery.percent if battery else 'Unknown'}%, Time: {datetime.datetime.now().strftime('%H:%M:%S')}, Internet: {'Connected' if any(iface.isup for iface in psutil.net_if_stats().values()) else 'Disconnected'}"

def execute_task(task, *args):
    task_functions = {
        "open": open_application,
        "volume": adjust_volume,
        "system status": lambda _: get_system_status(),
        "window": lambda action: keyboard.press_and_release({"minimize": "win+down", "maximize": "win+up", "switch": "alt+tab"}.get(action, "")),
        "media": lambda action: keyboard.press_and_release({"play": "playpause", "pause": "playpause", "stop": "stop"}.get(action, "")),
        "search": lambda query: webbrowser.open(f"https://www.google.com/search?q={query}"),
        "shortcut": lambda action: keyboard.press_and_release({"copy": "ctrl+c", "paste": "ctrl+v"}.get(action, "")),
        "mouse": lambda x, y: pyautogui.moveTo(x, y),
        "click": lambda _: pyautogui.click(),
    }
    return task_functions.get(task, lambda *_: "Invalid task.")(*args)
