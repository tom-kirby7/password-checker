import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import math
import random
import string

# --- Window Setup ---
root = ttk.Window(themename="journal")
root.title("Tom Kirby's Password Checker")
root.geometry("600x350")
root.minsize(400, 350)
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

# --- Variables ---
mode_var = ttk.StringVar(value="Strong")
length_var = ttk.IntVar(value=12)  # Default length

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

# --- Meter Update ---
def update_meter(percentage):
    meter_widget.configure(amountused=percentage)
    meter_widget.configure(subtext=f"{percentage:.0f}% Strength")

# --- Password Generator ---
def generate_strong_password():
    mode = mode_var.get()
    length = length_var.get()

    mode_settings = {
        "Easy":    (1, 1, 1, 0, 6.0),
        "Medium":  (2, 2, 2, 1, 7.5),
        "Strong":  (3, 3, 3, 3, 8.5)
    }

    lower_req, upper_req, digit_req, symbol_req, min_score = mode_settings[mode]

    min_required = lower_req + upper_req + digit_req + symbol_req
    if length < min_required:
        result_label.config(text=f"⚠️ Password length must be at least {min_required} for {mode} mode.")
        update_meter(0)
        return

    max_attempts = 500
    attempts = 0

    symbols_pool = "!@#$%^&*()-_=+[]{}|;:,.<>?"

    strict_bad_seqs = ["password", "123", "qwe"]

    while attempts < max_attempts:
        attempts += 1

        # Generate required characters
        lower = random.choices(string.ascii_lowercase, k=lower_req)
        upper = random.choices(string.ascii_uppercase, k=upper_req)
        digits = random.choices(string.digits, k=digit_req)
        symbols = random.choices(symbols_pool, k=symbol_req)

        remaining_len = length - min_required
        extras_pool = string.ascii_letters + string.digits + symbols_pool
        extras = random.choices(extras_pool, k=remaining_len)

        password_list = lower + upper + digits + symbols + extras
        random.shuffle(password_list)
        password = ''.join(password_list)

        # Check prohibited passwords
        if password in prohibited_passwords:
            continue

        # Check for strict sequences
        if any(seq in password.lower() for seq in strict_bad_seqs):
            continue

        score = total_score(password)
        if score >= min_score:
            password_entry.delete(0, 'end')
            password_entry.insert(0, password)
            check_password()
            return

    result_label.config(text="⚠️ Couldn't generate a strong password. Try again.")
    update_meter(0)

# --- Help/About Windows ---
def open_help_window():
    help_window = ttk.Toplevel(root)
    help_window.title("Help")
    help_window.geometry("350x220")
    help_text = (
        "Enter a password to check its strength.\n"
        "Scoring is based on:\n"
        "- Length\n"
        "- Character Variety\n"
        "- Entropy (Randomness)\n"
        "- Avoiding common sequences\n"
        "- Avoiding common passwords\n\n"
        "Use 'Generate Password' to create a strong password.\n"
        "Select Mode and Length for generation."
    )
    ttk.Label(help_window, text=help_text, font=("Segoe UI", 10), anchor="center", justify="center").pack(expand=True, pady=10, padx=10)
    ttk.Button(help_window, text="Close", command=help_window.destroy, bootstyle="primary").pack(pady=10)

def open_about_window():
    about_window = ttk.Toplevel(root)
    about_window.title("About")
    about_window.geometry("300x150")
    about_text = (
        "Tom Kirby's Password Checker\n"
        "Version 1.2\n\n"
        "Checks password strength\n"
        "based on modern standards."
    )
    ttk.Label(about_window, text=about_text, font=("Segoe UI", 10), anchor="center", justify="center").pack(expand=True, pady=20)
    ttk.Button(about_window, text="Close", command=about_window.destroy, bootstyle="primary").pack(pady=10)

# --- UI Layout ---

# Password Entry
password_entry = ttk.Entry(root, show="*", width=30, bootstyle="default")
password_entry.pack(pady=5)

def toggle_visibility():
    if password_entry.cget('show') == '*':
        password_entry.config(show='')
    else:
        password_entry.config(show='*')

ttk.Checkbutton(root, text="Show Password", command=toggle_visibility).pack(pady=2)

# Mode Selection
mode_frame = ttk.Frame(root)
mode_frame.pack(pady=5)
ttk.Label(mode_frame, text="Select Mode:").pack(side="left", padx=5)
mode_combo = ttk.Combobox(mode_frame, textvariable=mode_var, values=["Easy", "Medium", "Strong"], state="readonly", width=10)
mode_combo.pack(side="left", padx=5)

# Length Selection
length_frame = ttk.Frame(root)
length_frame.pack(pady=5)
ttk.Label(length_frame, text="Password Length:").pack(side="left", padx=5)
length_spinbox = ttk.Spinbox(length_frame, from_=6, to=30, textvariable=length_var, width=5)
length_spinbox.pack(side="left", padx=5)

# Buttons Frame (Help, About, Check Password)
buttons_frame = ttk.Frame(root)
buttons_frame.pack(pady=10, fill="x")

ttk.Button(buttons_frame, text="Help", command=open_help_window, bootstyle="secondary").pack(side='left', padx=10)
ttk.Button(buttons_frame, text="Check Password", command=check_password, bootstyle="primary").pack(side='left', padx=10)
ttk.Button(buttons_frame, text="About", command=open_about_window, bootstyle="secondary").pack(side='left', padx=10)

# Generate Password Button at bottom center
generate_frame = ttk.Frame(root)
generate_frame.pack(pady=10, fill="x")
ttk.Button(generate_frame, text="Generate Password", command=generate_strong_password, bootstyle="success").pack(anchor='center')

# Result Label
result_label = ttk.Label(root, text="Password Strength:", font=("Segoe UI", 14), anchor="center", justify="center")
result_label.pack(pady=5, padx=10, fill="x")

# Strength Meter
meter_widget = ttk.Meter(
    root,
    metersize=150,
    amountused=0,
    amounttotal=100,
    bootstyle="primary",
    subtext="Strength Meter"
)
meter_widget.pack(side='bottom', anchor='se', pady=10, padx=10)

# --- Start App ---
root.mainloop()
