import sys
import os

if sys.platform == "win32":
    os.environ ['TK_SILENCE_DEPRECATION'] = '1'
import customtkinter as ctk
import os
from auth import LoginWindow
from models import DB_FILE

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

if os.path.exists(DB_FILE):
    print("Removing old database file to fix schema issues...")
    
if __name__ == "__main__":
    login_window = LoginWindow()
    login_window.mainloop()