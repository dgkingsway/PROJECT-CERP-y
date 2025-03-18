import speech_recognition as sr
import logging
from typing import Optional
from automation import Automation
from logging.handlers import RotatingFileHandler

# Configure logging with rotation
handler = RotatingFileHandler('logs/cerp.log', maxBytes=5*1024*1024, backupCount=2)
logging.basicConfig(
    handlers=[handler],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SpeechProcessor:
    """Simplified class to handle speech recognition for CERP."""
    
    # Minimal error handling mapping
    ERROR_HANDLERS = {
        sr.WaitTimeoutError: lambda: (logging.warning("Listening timed out"), "Sorry, timed out waiting for command."),
        sr.UnknownValueError: lambda: (logging.warning("Could not understand audio"), "Sorry, I couldn't understand."),
        sr.RequestError: lambda: (logging.error("Speech recognition request failed"), "Could not request results, check internet connection."),
        OSError: lambda: (logging.error("Microphone not found"), "Error: Microphone not found, please check your audio settings."),
        Exception: lambda e: (logging.error(f"Speech recognition failed: {e}"), f"Error: {str(e)}")
    }
 
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.auto = Automation()
        logging.info("Speech processor initialized")

    def listen(self) -> Optional[str]:
        """Listen for a voice command and return the recognized text."""
        with sr.Microphone() as source:
            logging.info("Listening for command...")
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                command = self.recognizer.recognize_google(audio, language="en-US").lower()
                logging.info(f"Recognized command: {command}")
                return command
            except Exception as e:
                handler = self.ERROR_HANDLERS.get(type(e), lambda: (logging.error(f"Speech recognition failed: {e}"), f"Error: {str(e)}"))
                log_action, result = handler()
                return result

    # Command dispatcher (not used by GUI, kept for completeness)
    COMMAND_DISPATCHER = {
        "error": lambda cmd: cmd,
        "sorry": lambda cmd: cmd
    }

    def process_command(self, command: str) -> str:
        """Process the recognized command and return feedback using a dispatcher."""
        logging.info(f"Processing command: {command}")
        try:
            state_key = next((key for key in self.COMMAND_DISPATCHER if key in command.lower()), "default")
            return self.COMMAND_DISPATCHER.get(state_key, self._execute_command)(command)
        except Exception as e:
            logging.error(f"Command processing failed: {command}, Error: {e}")
            return f"Error processing command: {str(e)}"

    def _execute_command(self, command: str) -> str:
        """Execute a valid command."""
        try:
            words = command.split(maxsplit=1)
            task = words[0].lower() if words else ""
            args = words[1].split() if len(words) > 1 else []
            logging.info(f"Task: {task}, Args: {args}")
            result = self.auto.execute_task(task, *args)
            logging.info(f"Processed command: {command}, Result: {result}")
            return result
        except Exception as e:
            logging.error(f"Command execution failed: {command}, Error: {e}")
            return f"Error executing command: {str(e)}"
