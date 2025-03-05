import speech_recognition as sr
import automation

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"Recognized: {command}")

        # Process speech commands
        if "open" in command:
            app_name = command.replace("open ", "")
            return automation.execute_task("open", app_name)

        elif "volume up" in command or "increase volume" in command:
            return automation.execute_task("volume", 80)

        elif "volume down" in command or "decrease volume" in command:
            return automation.execute_task("volume", 30)

        elif "copy" in command:
            return automation.execute_task("shortcut", "copy")

        elif "paste" in command:
            return automation.execute_task("shortcut", "paste")

        elif "search" in command:
            query = command.replace("search ", "")
            return automation.execute_task("search", query)

        elif "move mouse" in command:
            return automation.execute_task("mouse", "move", 500, 500)

        elif "click" in command:
            return automation.execute_task("mouse", "click")

        else:
            return "Command not recognized."

    except sr.UnknownValueError:
        return "Sorry, I couldn't understand."
    except sr.RequestError:
        return "Could not request results, check internet."

