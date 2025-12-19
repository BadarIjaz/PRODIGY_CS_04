# PRODIGY_CS_04
## Task-04: Simple Keylogger

This repository contains a Python-based keylogger tool developed for ethical security analysis. It goes beyond basic input recording by tracking **Active Windows** and **Clipboard Content** to provide context-aware logs, simulating how real-world endpoint monitoring tools function.

### Usage
1. Run the script: `keylogger.py`
2. **Type** anywhere on your computer (Notepad, Browser, etc.).
3. **Copy (Ctrl+C)** any text to test the clipboard monitor.
4. **Press "Esc"** to safely stop the logger.
5. Check the newly created **`Keystroke_Logs`** folder for your timestamped log file.

### Watch the Demo Video
[Click to view the demo](https://badarijaz.github.io/PRODIGY_CS_04/keylogger_demo.mp4)

### Features & Logic
* **Context Awareness:** Logs the **Active Window Title** (e.g., "Google Chrome" vs "Notepad") using the Windows API (`ctypes`) to show *where* the user is typing.
* **Clipboard Forensics:** Automatically detects and logs text copied to the clipboard (`Ctrl+C`) using `pyperclip`, capturing "data-in-transit."
* **Stealth Buffering:** Uses a memory buffer (RAM) to store keystrokes temporarily and only writes to the disk every 20 keys, reducing system lag and detection risk.
* **Session Management:** Automatically creates a structured `Keystroke_Logs` directory and timestamps every file (e.g., `keylog_17-12-2025...txt`) to prevent data overwriting.
* **Standard Input Hooking:** Captures all alphanumeric keys and handles special keys (Space, Enter, Backspace) using the `pynput` library.

### Example

**Scenario 1: Typing in an App**
* **User Action:** Opens Notepad and types "Secret123"
* **Log Output:**
  ```text
  [WINDOW: Untitled - Notepad]
  Secret123


**Scenario 2: Copying Text**
* **User Action:** Highlights a URL and presses `Ctrl + C`
* **Log Output:**
  ```text
  [CLIPBOARD DETECTED]
  [https://www.google.com](https://www.google.com)
  [END CLIPBOARD]