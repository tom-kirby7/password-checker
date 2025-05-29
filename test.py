import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import math
import random
import string

# --- Window Setup ---
root = ttk.Window(themename="journal")
root.title("Tom Kirby's Password Checker")
root.geometry("600x350")  # increased height for the new button
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

# --- UI Variables for Mode and Length ---
mode_var = ttk.StringVar(value="Strong")  # Default to Strong
length_var = ttk.IntVar(value=16)          # Integer var for length display and logic
scale_var = ttk.DoubleVar(value=16)        # Double var for the scale widget

# Update length_var when scale moves, cast to int to avoid floats and lag
def on_scale_change(event=None):
    length_var.set(int(scale_var.get()))

# --- Password Generation ---
def generate_strong_password():
    mode = mode_var.get()
    length = length_var.get()

    # Define requirements per mode (lower, upper, digit, symbol, min score)
    mode_settings = {
        "Easy":    (1, 0, 0, 0, 3.0),  # Easy: minimal requirements, low score threshold
        "Medium":  (1, 1, 1, 0, 5.5),  # Medium: some uppercase/digits, moderate score
        "Strong":  (2, 2, 2, 2, 7.5),  # Strong: high char type requirements and high score
    }

    lower_req, upper_req, digit_req, symbol_req, min_score = mode_settings[mode]

    # Enforce minimum length per mode
    min_len_per_mode = {
        "Easy": 6,
        "Medium": 8,
        "Strong": 12,
    }
    if length < min_len_per_mode[mode]:
        length = min_len_per_mode[mode]
        length_var.set(length)
        scale_var.set(length)
        result_label.config(text=f"⚠️ Length increased to minimum {length} for {mode} mode.")

    total_required = lower_req + upper_req + digit_req + symbol_req
    if length < total_required:
        result_label.config(text=f"⚠️ Length must be at least {total_required} for {mode} mode.")
        update_meter(0)
        return

    attempts = 0
    while attempts < 100:
        attempts += 1

        lower = random.choices(string.ascii_lowercase, k=lower_req)
        upper = random.choices(string.ascii_uppercase, k=upper_req)
        digits = random.choices(string.digits, k=digit_req)
        symbols = random.choices("!@#$%^&*()-_=+[]{}|;:,.<>?", k=symbol_req)

        remaining_len = length - total_required
        extras = random.choices(
            string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?", 
            k=remaining_len
        )

        password_list = lower + upper + digits + symbols + extras
        random.shuffle(password_list)
        password = ''.join(password_list)

        if password in prohibited_passwords:
            continue
        if any(seq in password.lower() for seq in ["123", "234", "345", "abc", "qwe", "asd", "password"]):
            continue

        score = total_score(password)
        if score >= min_score:
            password_entry.delete(0, 'end')
            password_entry.insert(0, password)
            check_password()
            return

    result_label.config(text="⚠️ Couldn't generate a password meeting the criteria. Try again.")
    update_meter(0)


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

def toggle_visibility():
    if password_entry.cget('show') == '*':
        password_entry.config(show='')
    else:
        password_entry.config(show='*')

ttk.Checkbutton(root, text="Show Password", command=toggle_visibility).pack(pady=2)

ttk.Button(root, text="Check Password", command=check_password, bootstyle="primary").pack(pady=5)

# Add mode selection (Easy, Medium, Strong)
mode_frame = ttk.Frame(root)
mode_frame.pack(pady=5)

ttk.Label(mode_frame, text="Mode:").pack(side='left', padx=5)
for m in ["Easy", "Medium", "Strong"]:
    ttk.Radiobutton(mode_frame, text=m, variable=mode_var, value=m).pack(side='left')

# Add length selection slider with improved handling
length_frame = ttk.Frame(root)
length_frame.pack(pady=5)

ttk.Label(length_frame, text="Length:").pack(side='left', padx=5)

length_scale = ttk.Scale(length_frame, from_=6, to=32, variable=scale_var, orient='horizontal', length=150, command=lambda e: on_scale_change())
length_scale.pack(side='left')

length_display = ttk.Label(length_frame, textvariable=length_var)
length_display.pack(side='left', padx=5)

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

# Buttons frame for Help and About (fixed visibility & placement)
button_frame = ttk.Frame(root)
button_frame.pack(side='bottom', anchor='w', pady=10, padx=10)

ttk.Button(button_frame, text="Help", command=open_help_window, bootstyle="secondary").pack(side='left', padx=5)
ttk.Button(button_frame, text="About", command=open_about_window, bootstyle="secondary").pack(side='left', padx=5)

# Generate password button centered at bottom
generate_button = ttk.Button(root, text="Generate Password", command=generate_strong_password, bootstyle="success")
generate_button.pack(side='bottom', pady=10)

# Start App
root.mainloop()
