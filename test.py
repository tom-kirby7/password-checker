import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import math

# --- Window Setup ---
root = ttk.Window(themename="journal")
root.title("Tom Kirby's Password Checker")
root.geometry("600x300")
root.minsize(200, 200)
root.maxsize(1000, 1000)

# --- Load Prohibited Passwords ---
def load_prohibited_passwords(filename):
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
            return set(line.strip() for line in file if line.strip())
    except FileNotFoundError:
        print(f"Warning: '{filename}' not found.")
        return set()

prohibited_passwords = load_prohibited_passwords('prohibited.txt')

# --- Scoring Functions ---
def score_length(password):
    length = len(password)
    return min(length * 0.5, 10)  # Max 10 points

def score_variety(password):
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(not c.isalnum() for c in password)
    types_used = sum([has_lower, has_upper, has_digit, has_symbol])
    return {1: 2.5, 2: 5, 3: 7.5, 4: 10}.get(types_used, 0)

def score_entropy(password):
    charset_size = 0
    if any(c.islower() for c in password): charset_size += 26
    if any(c.isupper() for c in password): charset_size += 26
    if any(c.isdigit() for c in password): charset_size += 10
    if any(not c.isalnum() for c in password): charset_size += 33
    if charset_size == 0 or len(password) == 0:
        return 0
    entropy = len(password) * math.log2(charset_size)
    return min(entropy / 6, 10)  # Normalize to 10

def score_keyboard_sequence(password):
    common_seqs = ["123", "234", "345", "abc", "qwe", "asd", "password"]
    return -5 if any(seq in password.lower() for seq in common_seqs) else 0

def total_score(password):
    return (
        score_length(password) * 0.3 +
        score_variety(password) * 0.3 +
        score_entropy(password) * 0.3 +
        score_keyboard_sequence(password) * 0.1
    )

def strength_label(score):
    if score <= 3:
        return "Very Weak"
    elif score <= 5:
        return "Weak"
    elif score <= 7:
        return "Moderate"
    elif score <= 8.5:
        return "Strong"
    else:
        return "Very Strong"

# --- Meter Update ---
def update_meter(percentage):
    meter_widget.configure(amountused=percentage)
    meter_widget.configure(subtext=f"{percentage:.0f}% Strength")

# --- Password Evaluation ---
def check_password():
    password = password_entry.get()
    if not password:
        result_label.config(text="❌ Please enter a password.")
        update_meter(0)
        return

    if password in prohibited_passwords:
        result_label.config(text="❌ This password is too common or not allowed.")
        update_meter(0)
        return

    score = total_score(password)
    label = strength_label(score)
    result_label.config(text=f"Password Strength: {label}")
    update_meter(min(score * 10, 100))  # Scale score to percentage

# --- Help/About Windows ---
def open_help_window():
    help_window = ttk.Toplevel(root)
    help_window.title("Help")
    help_window.geometry("300x200")

    help_text = (
        "Enter a password to check its strength.\n"
        "Scoring is based on:\n"
        "- Length\n"
        "- Character Variety\n"
        "- Entropy (Randomness)\n"
        "- Avoiding common sequences\n"
        "- Avoiding common passwords"
    )

    ttk.Label(help_window, text=help_text, font=("Segoe UI", 10), anchor="center", justify="center").pack(expand=True, pady=20)
    ttk.Button(help_window, text="Close", command=help_window.destroy, bootstyle="primary").pack(pady=10)

def open_about_window():
    about_window = ttk.Toplevel(root)
    about_window.title("About")
    about_window.geometry("300x150")

    about_text = (
        "Tom Kirby's Password Checker\n"
        "Version 1.1\n\n"
        "Checks password strength\n"
        "based on modern standards."
    )

    ttk.Label(about_window, text=about_text, font=("Segoe UI", 10), anchor="center", justify="center").pack(expand=True, pady=20)
    ttk.Button(about_window, text="Close", command=about_window.destroy, bootstyle="primary").pack(pady=10)

# --- UI Layout ---
password_entry = ttk.Entry(root, show="*", width=30, bootstyle="default")
password_entry.pack(pady=5)

ttk.Button(root, text="Check Password", command=check_password, bootstyle="primary").pack(pady=5)

result_label = ttk.Label(root, text="Password Strength:", font=("Segoe UI", 14), anchor="center", justify="center")
result_label.pack(pady=5, padx=10, fill="x")

meter_widget = ttk.Meter(
    root,
    metersize=150,
    amountused=0,
    amounttotal=100,
    bootstyle="primary",
    subtext="Strength Meter"
)
meter_widget.pack(side='bottom', anchor='se', pady=10, padx=10)

button_frame = ttk.Frame(root)
button_frame.pack(side='bottom', anchor='w', pady=10, padx=10)

ttk.Button(button_frame, text="Help", command=open_help_window, bootstyle="secondary").pack(side='left', padx=5)
ttk.Button(button_frame, text="About", command=open_about_window, bootstyle="secondary").pack(side='left', padx=5)

# --- Start App ---
root.mainloop()
