import ttkbootstrap as ttk
from ttkbootstrap.constants import *
 
def open_new_window():
    # Create a new top-level window
    new_win = ttk.Toplevel()
    new_win.title("New Window")
    new_win.geometry("300x200")
 
    # Add content to the new window
    label = ttk.Label(new_win, text="This is a new window!", bootstyle=INFO)
    label.pack(pady=20)
 
    close_button = ttk.Button(new_win, text="Close", command=new_win.destroy, bootstyle=SUCCESS)
    close_button.pack(pady=10)
 
# Create the main application window
root = ttk.Window(themename="superhero")
root.title("Main Window")
root.geometry("400x300")
 
# Add a button to open a new window
open_button = ttk.Button(root, text="Open New Window", command=open_new_window, bootstyle=PRIMARY)
open_button.pack(pady=50)
 
root.mainloop()