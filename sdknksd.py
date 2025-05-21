import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Create main window
root = ttk.Window(themename="cyborg", title="Main App", size=(400, 200))

# Function to open a new pop-up window
def open_about_window():
    about_window = ttk.Toplevel(root)
    about_window.title("About")
    about_window.geometry("300x150")

    # Label inside the new window
    info_label = ttk.Label(
        about_window,
        text="Password Checker v1.0\nCreated by Tom Kirby",
        font=("Segoe UI", 12),
        foreground="white",
        background=about_window.cget("background")  # Match theme background
    )
    info_label.pack(pady=20)

# Button in the main window
about_button = ttk.Button(
    root,
    text="About",
    command=open_about_window,
    bootstyle="info"
)
about_button.pack(pady=50)

# Start the app
root.mainloop()
