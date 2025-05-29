import ttkbootstrap as ttk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
import math


root = ttk.Window(themename="superhero")  # Use 'flatly' theme for a modern look
root.title("Tom Kirby's Password Checker")
root.configure(background="black")
root.minsize(200, 200)
root.maxsize(1000, 1000)
root.geometry("600x300")
 

def length_score(password):
    length = len(password)
    if length == 0:
        return 0
    elif length <= 4:
        return 2
    elif length <= 7:
        return 4
    elif length <= 10:
        return 6
    elif length <= 14:
        return 8
    else:
        return 10

def variety_score(password):
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(not c.isalnum() for c in password)
    types_used = sum([has_lower, has_upper, has_digit, has_symbol])

    if types_used == 1:
        return 2
    elif types_used == 2:
        return 5
    elif types_used == 3:
        return 8
    elif types_used == 4:
        return 10
    return 0

def calculate_entropy(password):
    escore = 0
    if any(c.islower() for c in password): escore += 26
    if any(c.isupper() for c in password): escore += 26
    if any(c.isdigit() for c in password): escore += 10
    if any(not c.isalnum() for c in password): escore += 33
    if escore == 0 or len(password) == 0:
        return 0
    return len(password) * math.log2(escore)

def calculate_strength(password):
    length = length_score(password)
    variety = variety_score(password)
    total_strength = length + variety
    if total_strength <= 0:
        return "Enter a password"
    elif total_strength <= 5:
        return "Weak"
    elif total_strength <= 10:
        return "Moderate"
    elif total_strength <= 15:
        return "Strong"
    else:
        return "Very Strong"

# -------------------------
# Load prohibited passwords
# -------------------------

def load_prohibited_passwords(filename):
    with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
        return set(line.strip() for line in file if line.strip())

prohibited_passwords = load_prohibited_passwords('prohibited.txt')

# -------------------------
# Password check function
# -------------------------
# Removed global percentage calculation as total_strength is not defined globally

def update_meter(percentage):
    # Update the meter widget with the calculated percentage
    meter_widget.configure(amountused=percentage)
    meter_widget.configure(subtext=f"{percentage:.0f}% Strength")  # Display percentage as subtext

def check_password():
    password = password_entry.get()
    if not password:
        result_label.config(text="❌ Please enter a password.")
        update_meter(0)  # Update meter for empty password
        return
    if password in prohibited_passwords:
        result_label.config(text="❌ This password is too common or not allowed.")
        update_meter(0)  # Update meter for prohibited password
        return
    strength = calculate_strength(password)
    percentage = (length_score(password) + variety_score(password)) / 20 * 100  # Calculate percentage locally
    result_label.config(text=f"Password Strength: {strength}")
    update_meter(percentage)  # Update meter based on calculated percentage

# -------------------------
# GUI Widgets
# -------------------------
def open_help_window():
    help_window = ttk.Toplevel(root)  # Create a new top-level window
    help_window.title("Help")
    help_window.geometry("300x200")
    help_window.configure(background="black")  # Set background color

    # Add content to the Help window
    help_label = ttk.Label(
        help_window,
        text="Enter a password to check its strength.\n"
             "The app checks for length, variety,\n"
             "and common passwords.",
        font=("Segoe UI", 10),
        background="black"
    )
    help_label.pack(expand=True, pady=20)

    # Add a close button
    close_button = ttk.Button(
        help_window,
        text="Close",
        command=help_window.destroy,
        bootstyle=SUCCESS
    )
    close_button.pack(pady=10)
def open_about_window():
    about_window = ttk.Toplevel(root)  # Create a new top-level window
    about_window.title("About")
    about_window.geometry("300x150")
    about_window.configure(background="black")  # Set background color

    # Add content to the About window
    about_label = ttk.Label(
        about_window,
        text="Tom Kirby's Password Checker\nVersion 1.0\nThis app checks password strength\nand prevents common passwords.",
        font=("Segoe UI", 10),
        background="black"
    )
    about_label.pack(expand=True, pady=20)

    # Add a close button
    close_button = ttk.Button(
        about_window,
        text="Close",
        command=about_window.destroy,
        bootstyle=SUCCESS
    )
    close_button.pack(pady=10)

password_entry = ttk.Entry(root, show="*", width=30)
password_entry.pack(pady=5)

check_button = ttk.Button(root, text="Check Password", command=check_password, bootstyle=SUCCESS)
check_button.pack(pady=5)

# Adjust the position of the strength label
result_label = ttk.Label(
    root,
    text="Password Strength:",
    font=("Segoe UI", 14),
    foreground="white",
    background=root.cget("background"),
    anchor="w"  # Align text to the left
)
result_label.pack(pady=5, padx=10, fill="x")  # Adjust padding and fill horizontally

# Add a meter widget to display password strength percentage
meter_widget = ttk.Meter(
    root,
    metersize=150,  # Increased size
    amountused=0,
    amounttotal=100,
    bootstyle="primary",  # Changed style to remove blue box
    subtext="Strength Meter",
)
meter_widget.pack(side='bottom', anchor='e', pady=10, padx=10)  # Positioned at the bottom-right

# Create a frame to hold the "About" and "Help" buttons at the bottom-left
button_frame = ttk.Frame(root)
button_frame.pack(side='bottom', anchor='w', pady=10, padx=10)

# Add the "Help" and "About" buttons to the frame
ttk.Button(button_frame, text="Help", command=open_help_window, bootstyle=SECONDARY).pack(side='left', padx=5)
ttk.Button(button_frame, text="About", command=open_about_window, bootstyle=SUCCESS).pack(side='left', padx=5)

root.mainloop()