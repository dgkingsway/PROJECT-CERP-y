# CERP-y - Computer Automation for Disabled People Using Python

## Overview
CERP (Computer Automation for Disabled People) is a voice-activated automation tool designed to assist individuals with motor disabilities in operating a computer more efficiently. By integrating voice commands, automation, and accessibility features, CERP enhances usability for those with limited mobility.

## Features

### 1️⃣ **Core Automation Features**
- **Open Applications** – Notepad, Calculator, Chrome, and more
- **System Volume Control** – Increase, Decrease, Set specific volume levels
- **Brightness Control** – Adjust screen brightness (Windows-based)
- **Keyboard Shortcuts** – Copy, Paste, Minimize, Close Windows
- **Web Search Automation** – Execute Google searches via voice
- **Mouse Control** – Move cursor, Click, Right-click, Double-click

### 2️⃣ **Voice Control & Wake Word Activation**
- **Speech Recognition** – Supports Vosk (Offline), Google, and Whisper
- **Wake Word Activation** – "Hey Cerp" using Porcupine
- **Global Voice Activation** – Runs continuously until shutdown
- **Customizable Voice Commands** – Users can modify commands to suit their needs

### 3️⃣ **Graphical User Interface (GUI)**
- **Developed with PyQt6** – Provides a modern UI for ease of use
- **Mic Icon for Voice Control** – Replaces traditional text-based buttons
- **Optimized Layout & Visibility Fixes** – Ensures accessibility and usability

### 4️⃣ **Code Optimization & Structure**
- **Minimized `if-else` Usage** – Used function mapping for cleaner logic
- **Modular Codebase** – Separated automation logic into `automation.py`
- **Scalability & Maintainability** – Designed for future feature expansion

## Installation

### **Prerequisites**
- Python 3.12+
- Required Python Libraries:
  ```sh
  pip install pyqt6 pyautogui keyboard speechrecognition pvporcupine
  ```

### **Setup**
1. Clone the repository:
   ```sh
git clone https://github.com/dgkingsway/PROJECT-CERP-y.git
   ```
2. Navigate to the project folder:
   ```sh
   cd PROJECT-CERP-y
   ```
3. Run the application:
   ```sh
   python gui.py
   ```

## Usage
- Start CERP and say **"Hey Cerp"** to activate voice commands.
- Give commands such as **"Open Notepad"**, **"Increase Volume"**, or **"Search AI Technology"**.
- Use the GUI for manual control and accessibility settings.

## Future Enhancements
- **Auto Start on Boot** – Enable CERP to run at system startup
- **Additional Accessibility Features to be added** – Gesture recognition, eye-tracking support
- **Customizable Commands & Profiles** – Enhanced personalization options

## Contributors

We appreciate contributions from everyone! Thanks to the following contributors:

- **[dgkingsway](https://github.com/dgkingsway)**
- **[dark blind](https://github.com/ala527)**
- **[smoking red](https://github.com/AlwinJs)**

Want to contribute? Check out our [Contributing Guidelines](CONTRIBUTING.md).


## License
This project is licensed under the [MIT License](LICENSE).

## Contributing
Feel free to contribute by submitting pull requests or raising issues.

## Contact
For questions or suggestions, reach out via GitHub Issues or email [dgkingsway@gmail.com](mailto:dgkingsway@gmail.com).

> ⚠️ **Disclaimer:** This project is not affiliated with any other "CERP" projects. See the full disclaimer below.
