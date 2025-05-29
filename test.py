import ttkbootstrap as ttk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
import math


root = ttk.Window(themename="superhero")  # Use 'flatly' theme for a modern look
root.title("Tom Kirby's Password Checker")
root.configure(background="black")
root.minsize(200, 200)
root.maxsize(1000, 1000)
root.geometry("600x300+100+100")


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

def check_password():
    password = password_entry.get()
    if not password:
        result_label.config(text="❌ Please enter a password.")
        return
    if password in prohibited_passwords:
        result_label.config(text="❌ This password is too common or not allowed.")
        return
    strength = calculate_strength(password)
    result_label.config(text=f"✅ Password Strength: {strength}")

# -------------------------
# GUI Widgets
# -------------------------

def open_about_window():
    about_window = ttk.Toplevel(root)  # Create a new top-level window
    about_window.title("About")
    about_window.geometry("300x150")
    about_window.configure(background="white")  # Set background color

    # Add content to the About window
    about_label = ttk.Label(
        about_window,
        text="Tom Kirby's Password Checker\nVersion 1.0\nThis app checks password strength\nand prevents common passwords.",
        font=("Segoe UI", 10),
        justify="center",
        background=""
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

about_button = ttk.Button(root, text="About", command=open_about_window, bootstyle=SUCCESS).pack(side='left', padx=5, pady=10)

password_entry = ttk.Entry(root, show="*", width=30)
password_entry.pack(pady=5)

check_button = ttk.Button(root, text="Check Password", command=check_password, bootstyle=SUCCESS)
check_button.pack(pady=5)

result_label = ttk.Label(root, text="Password Strength:", font=("Segoe UI", 14),
foreground="white", background=root.cget("background"))
result_label.pack(pady=5)

ttk.Button(root, text="Help", style='secondary.TButton').pack(side='left', padx=5, pady=10)


root.mainloop()