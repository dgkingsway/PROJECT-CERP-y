import speech_recognition as sr
import logging
from typing import Optional
from automation import Automation
from logging.handlers import RotatingFileHandler
import os

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

class SpeechProcessor:
    """Handles speech recognition and command processing with improved delegation."""

    ERROR_HANDLERS = {
        sr.WaitTimeoutError: lambda: (logging.warning("Listening timed out"), "Sorry, timed out waiting for command."),
        sr.UnknownValueError: lambda: (logging.warning("Could not understand audio"), "Sorry, I couldn't understand."),
        sr.RequestError: lambda: (logging.error("Speech recognition request failed"), "Could not request results, check internet."),
        OSError: lambda: (logging.error("Microphone not found"), "Error: Microphone not found, check audio settings."),
        Exception: lambda e: (logging.error(f"Speech recognition failed: {e}"), f"Error: {str(e)}")
    }

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.auto = Automation()
        logging.info("Speech processor initialized")
        self.COMMAND_DISPATCHER = {
            "error": lambda cmd: cmd,
            "sorry": lambda cmd: cmd,
            "open": lambda cmd: self.auto.execute_task(cmd),
            "close": lambda cmd: self.auto.execute_task(cmd),
            "increase volume": lambda cmd: self.auto.execute_task(cmd),
            "decrease volume": lambda cmd: self.auto.execute_task(cmd),
            "system status": lambda cmd: self.auto.execute_task(cmd),
            "start voice typing": lambda cmd: self.auto.execute_task(cmd),
            "stop voice typing": lambda cmd: self.auto.execute_task(cmd),
            "skip shorts": lambda cmd: self.auto.execute_task(cmd),
            "skip next": lambda cmd: self.auto.execute_task(cmd),
            "exit": lambda cmd: self.auto.execute_task(cmd),
        }

    def listen(self) -> Optional[str]:
        """Capture voice command with robust error handling."""
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

    def process_command(self, command: str) -> str:
        """Process commands, delegating to Automation where applicable."""
        logging.info(f"Processing command: {command}")
        try:
            state_key = next((key for key in self.COMMAND_DISPATCHER if key in command.lower()), "default")
            return self.COMMAND_DISPATCHER.get(state_key, self._execute_command)(command)
        except Exception as e:
            logging.error(f"Command processing failed: {command}, Error: {e}")
            return f"Error processing command: {str(e)}"

    def _execute_command(self, command: str) -> str:
        """Execute non-specific commands via Automation."""
        try:
            return self.auto.execute_task(command)
        except Exception as e:
            logging.error(f"Command execution failed: {command}, Error: {e}")
            return f"Error executing command: {str(e)}"

if __name__ == "__main__":
    processor = SpeechProcessor()
    command = processor.listen()
    print(processor.process_command(command))