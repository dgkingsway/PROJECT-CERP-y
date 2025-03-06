import speech_recognition as sr
import automation

# Mapping speech commands to actions
command_map = {
    "open": lambda cmd: automation.execute_task("open", cmd.replace("open ", "")),
    "volume up": lambda _: automation.execute_task("volume", 80),
    "increase volume": lambda _: automation.execute_task("volume", 80),
    "volume down": lambda _: automation.execute_task("volume", 30),
    "decrease volume": lambda _: automation.execute_task("volume", 30),
    "copy": lambda _: automation.execute_task("shortcut", "copy"),
    "paste": lambda _: automation.execute_task("shortcut", "paste"),
    "search": lambda cmd: automation.execute_task("search", cmd.replace("search ", "")),
    "move mouse": lambda _: automation.execute_task("mouse", "move", 500, 500),
    "click": lambda _: automation.execute_task("mouse", "click"),
}

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"Recognized: {command}")

        # Find matching command
        for key in command_map:
            if key in command:
                return command_map[key](command)
        
        return "Command not recognized."

    except sr.UnknownValueError:
        return "Sorry, I couldn't understand."
    except sr.RequestError:
        return "Could not request results, check internet."
