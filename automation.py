import os
import webbrowser
import pyautogui
import keyboard
import subprocess
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL

# Function to open applications
def open_application(app_name):
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    }
    if app_name in apps:
        subprocess.Popen(apps[app_name])
        return f"Opening {app_name}..."
    else:
        return f"Application {app_name} not found."

# Function to adjust volume
def adjust_volume(level):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    volume.SetMasterVolumeLevelScalar(level / 100, None)
    return f"Volume set to {level}%."

# Function to adjust brightness (Windows only)
def adjust_brightness(level):
    os.system(f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})")
    return f"Brightness set to {level}%."

# Function for keyboard shortcuts
def perform_shortcut(action):
    shortcuts = {
        "copy": "ctrl+c",
        "paste": "ctrl+v",
        "minimize": "win+d",
        "close": "alt+f4",
    }
    if action in shortcuts:
        keyboard.press_and_release(shortcuts[action])
        return f"Performed {action}."
    else:
        return f"Shortcut {action} not found."

# Function to search the web
def search_google(query):
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return f"Searching Google for '{query}'..."

# Function for mouse control
def mouse_control(action, x=None, y=None):
    actions = {
        "click": pyautogui.click,
        "double click": pyautogui.doubleClick,
        "right click": pyautogui.rightClick,
    }
    if action in actions:
        if x is not None and y is not None:
            actions[action](x, y)
        else:
            actions[action]()
        return f"Mouse {action} performed."
    elif action == "move":
        pyautogui.moveTo(x, y, duration=0.5)
        return f"Mouse moved to {x}, {y}."
    else:
        return "Invalid mouse action."

# Function to execute automation tasks
def execute_task(task, value=None, x=None, y=None):
    if task == "open":
        return open_application(value)
    elif task == "volume":
        return adjust_volume(value)
    elif task == "brightness":
        return adjust_brightness(value)
    elif task == "shortcut":
        return perform_shortcut(value)
    elif task == "search":
        return search_google(value)
    elif task == "mouse":
        return mouse_control(value, x, y)
    else:
        return "Invalid task."

