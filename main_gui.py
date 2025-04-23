import tkinter as tk
import threading
import os
from PIL import Image, ImageTk  

# Functions to run each feature
def run_virtual_mouse():
    os.system("python mouse.py")

def run_voice_assistant():
    os.system("python app.py")

# Launch each in a new thread to keep GUI responsive
def start_mouse_thread():
    threading.Thread(target=run_virtual_mouse).start()

def start_voice_thread():
    threading.Thread(target=run_voice_assistant).start()

# Button hover effects
def on_enter(button):
    button['bg'] = '#45a049'  # Darker green for mouse button
    button['activebackground'] = '#45a049'

def on_leave(button):
    button['bg'] = '#4CAF50'  # Original green for mouse button
    button['activebackground'] = '#4CAF50'

def on_enter_voice(button):
    button['bg'] = '#1e88e5'  # Darker blue for voice button
    button['activebackground'] = '#1e88e5'

def on_leave_voice(button):
    button['bg'] = '#2196F3'  # Original blue for voice button
    button['activebackground'] = '#2196F3'

# GUI setup
root = tk.Tk()
root.title("Voice & Gesture Control")
root.geometry("400x250")
root.configure(bg="#222")

# Load background image using Pillow
bg_image = Image.open("images/bg2.jpg")  # Load the image
bg_image = bg_image.resize((400, 250), Image.LANCZOS)  # Resize the image to fit the window
bg_image_tk = ImageTk.PhotoImage(bg_image)  # Convert to PhotoImage for Tkinter

bg_label = tk.Label(root, image=bg_image_tk)
bg_label.place(relwidth=1, relheight=1)

# Animated title
title = tk.Label(root, text="Control Your PC", font=("Helvetica", 18, "bold"), fg="white", bg="#222")
title.pack(pady=20)

def animate_title():
    for i in range(10):
        title.config(fg=f"#{i*25:02x}00{(10-i)*25:02x}")
        root.update()
        root.after(100)
    title.config(fg="white")  # Reset to white

animate_title()

# Rounded button creation
def create_rounded_button(text, command, hover_in, hover_out):
    button = tk.Button(root, text=text, font=("Arial", 14), command=command, bg="#4CAF50", fg="white", padx=20, pady=10)
    button.bind("<Enter>", lambda e: hover_in(button))
    button.bind("<Leave>", lambda e: hover_out(button))
    return button

btn_mouse = create_rounded_button("🖱️ Start Virtual Mouse", start_mouse_thread, on_enter, on_leave)
btn_mouse.pack(pady=10)

btn_voice = create_rounded_button("🎙️ Start Voice Assistant", start_voice_thread, on_enter_voice, on_leave_voice)
btn_voice.pack(pady=10)

exit_btn = tk.Button(root, text="❌ Exit", font=("Arial", 12), command=root.quit, bg="red", fg="white")
exit_btn.pack(pady=20)

root.mainloop()