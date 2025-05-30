import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import math
import random
import string

root = ttk.Window(themename="journal")
root.title("Tom Kirby's Password Checker")
root.geometry("720x520")
root.minsize(450, 350)

# --- Variables ---
mode_var = ttk.StringVar(value="Medium")  # For generation mode
length_var = ttk.IntVar(value=12)         # For generation length
show_password_var = ttk.BooleanVar(value=False)
generate_mode_var = ttk.BooleanVar(value=False)  # Whether user wants to generate password

# --- Load prohibited passwords ---
def load_prohibited_passwords(filename):
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
            return set(line.strip() for line in file if line.strip())
    except FileNotFoundError:
        print(f"Warning: '{filename}' not found.")
        return set()

prohibited_passwords = load_prohibited_passwords('prohibited.txt')

# --- Scoring Functions ---ewrm
def score_length(password): 
    return min(len(password) * 0.5, 10)

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
    if charset_size == 0 or len(password) == 0: return 0
    entropy = len(password) * math.log2(charset_size)
    return min(entropy / 6, 10)

def score_keyboard_sequence(password):
    common_seqs = ["123", "234", "345", "456", "567", "678", "789", "890",
                   "abc", "bcd", "cde", "def", "efg", "fgh", "ghi", "hij",
                   "qwe", "wer", "ert", "rty", "tyu", "yui", "uio", "iop",
                   "asd", "sdf", "dfg", "fgh", "ghj", "hjk", "jkl",
                   "zxc", "xcv", "cvb", "vbn", "bnm",
                   "password", "letmein", "admin", "welcome"]
    for seq in common_seqs:
        if seq in password.lower():
            return 5  # penalty points
    return 0

def total_score(password):
    length_score = score_length(password)
    variety_score = score_variety(password)
    entropy_score = score_entropy(password)
    seq_penalty = score_keyboard_sequence(password)

    base_score = (
        length_score +
        variety_score +
        entropy_score
    )
    total = base_score - seq_penalty
    return max(min(total, 30), 0), length_score, variety_score, entropy_score, seq_penalty

def strength_label(score):
    if score <= 9: return "Very Weak"
    elif score <= 15: return "Weak"
    elif score <= 21: return "Moderate"
    elif score <= 25.5: return "Strong"
    else: return "Very Strong"

# --- Color Helper ---
def get_bootstyle(score, penalty=False):
    if penalty:
        return "danger"
    if score <= 9:
        return "danger"
    elif score <= 15:
        return "warning"
    elif score <= 21:
        return "info"
    else:
        return "success"

def meter_bootstyle(score):
    if score <= 9:
        return "danger"
    elif score <= 15:
        return "warning"
    elif score <= 21:
        return "info"
    else:
        return "success"

# --- Password Generator ---
def perform_generate_password():
    mode = mode_var.get()
    length = length_var.get()

    if mode == "Easy":
        charset = string.ascii_lowercase
        min_types = 1
        min_score = 10  # Adjusted minimum score for perfect passwords
    elif mode == "Medium":
        charset = string.ascii_letters + string.digits
        min_types = 2
        min_score = 20  # Adjusted minimum score for perfect passwords
    else:
        charset = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
        min_types = 4
        min_score = 30  # Adjusted minimum score for perfect passwords

    attempts = 0
    while attempts < 100:
        attempts += 1
        password_chars = []

        if mode == "Easy":
            password_chars += random.choices(string.ascii_lowercase, k=length)
        elif mode == "Medium":
            password_chars += random.choices(string.ascii_lowercase, k=max(1, length // 3))
            password_chars += random.choices(string.ascii_uppercase, k=max(1, length // 4))
            password_chars += random.choices(string.digits, k=max(1, length // 4))
            remaining = length - len(password_chars)
            password_chars += random.choices(charset, k=remaining)
        else:
            reqs = {
                string.ascii_lowercase: 2,
                string.ascii_uppercase: 2,
                string.digits: 2,
                "!@#$%^&*()-_=+[]{}|;:,.<>?": 2,
            }
            for chars, count in reqs.items():
                password_chars += random.choices(chars, k=count)
            remaining = length - len(password_chars)
            password_chars += random.choices(charset, k=remaining)

        random.shuffle(password_chars)
        password = ''.join(password_chars[:length])

        if password in prohibited_passwords: continue
        if any(seq in password.lower() for seq in ["123", "abc", "password", "qwe"]): continue

        types_used = sum([
            any(c.islower() for c in password),
            any(c.isupper() for c in password),
            any(c.isdigit() for c in password),
            any(not c.isalnum() for c in password),
        ])
        if types_used < min_types: continue

        score, _, _, _, seq_penalty = total_score(password)
        if score >= min_score and seq_penalty == 0:
            password_entry.delete(0, 'end')
            password_entry.insert(0, password)
            check_password()
            return

    result_label.config(text="⚠️ Couldn't generate a password meeting the criteria. Try again.")
    update_meter(0, "danger")

# --- Meter Update ---
def update_meter(score, style):
    percentage = (score / 30) * 100  # Adjust percentage calculation to reflect the total score accurately
    meter_widget.configure(amountused=percentage)
    meter_widget.configure(bootstyle=style)
    meter_widget.configure(subtext=f"{percentage:.0f}% Strength")

# --- Password Evaluation ---
def check_password(event=None):
    password = password_entry.get()
    if not password:
        result_label.config(text="❌ Please enter a password.")
        update_meter(0, "danger")
        clear_category_scores()
        return

    if password in prohibited_passwords:
        result_label.config(text="❌ This password is too common or not allowed.")
        update_meter(0, "danger")
        clear_category_scores()
        return

    score, len_score, var_score, ent_score, seq_penalty = total_score(password)
    label = strength_label(score)

    penalty_msg = ""
    if seq_penalty > 0:
        penalty_msg = " (Penalty applied for common sequences!)"

    result_label.config(text=f"Password Strength: {label}{penalty_msg}")
    update_meter(score, meter_bootstyle(score))

    update_category_scores(len_score, var_score, ent_score, seq_penalty)

def clear_category_scores():
    for bar, label in [(length_bar, length_score_label), 
                       (variety_bar, variety_score_label), 
                       (entropy_bar, entropy_score_label), 
                       (sequence_bar, sequence_score_label)]:
        bar.configure(value=0, bootstyle="secondary")
        label.config(text="0")

def update_category_scores(len_score, var_score, ent_score, seq_penalty):
    length_bar.configure(value=len_score, bootstyle=get_bootstyle(len_score))
    variety_bar.configure(value=var_score, bootstyle=get_bootstyle(var_score))
    entropy_bar.configure(value=ent_score, bootstyle=get_bootstyle(ent_score))
    sequence_bar.configure(value=seq_penalty, bootstyle=get_bootstyle(seq_penalty, penalty=True))

    length_score_label.config(text=f"{int(len_score)}")
    variety_score_label.config(text=f"{int(var_score)}")
    entropy_score_label.config(text=f"{int(ent_score)}")
    sequence_score_label.config(text=f"-{int(seq_penalty)}" if seq_penalty else "0")

# --- Show / Hide Password ---
def toggle_password_visibility():
    if show_password_var.get():
        password_entry.configure(show="")
    else:
        password_entry.configure(show="•")

# --- Copy Password to Clipboard ---
def copy_to_clipboard():
    password = password_entry.get()
    if password:
        root.clipboard_clear()
        root.clipboard_append(password)
        root.update()  # now it stays on the clipboard after the window is closed

# --- Help & About ---
def show_help():
    help_window = ttk.Toplevel(root)  # Create a new top-level window
    help_window.title("Help")
    help_window.geometry("400x200")
    help_window.configure(background="white")  # Set background color

    help_label = ttk.Label(
        help_window,
        text="Enter a password to check its strength.\n"
             "Password strength is scored on length, variety, entropy, and penalties for common sequences.\n\n"
             "To generate a password, check 'Generate Password' and adjust the settings.\n"
             "Then click Generate to create a secure password.",
        font=("Segoe UI", 10),
        background="white",
        justify="left"
    )
    help_label.pack(expand=True, fill=BOTH, padx=10, pady=10)

    close_button = ttk.Button(help_window, text="Close", command=help_window.destroy, bootstyle="primary")
    close_button.pack(pady=10)

def show_about():
    about_window = ttk.Toplevel(root)  # Create a new top-level window
    about_window.title("About")
    about_window.geometry("400x150")
    about_window.configure(background="white")  # Set background color

    about_label = ttk.Label(
        about_window,
        text="Password Checker v1.0\n"
             "Created by Tom Kirby\n"
             "This tool helps evaluate password strength and generate secure passwords.",
        font=("Segoe UI", 10),
        background="white",
        justify="center"
    )
    about_label.pack(expand=True, fill=BOTH, padx=10, pady=10)

    close_button = ttk.Button(about_window, text="Close", command=about_window.destroy, bootstyle="primary")
    close_button.pack(pady=10)

# --- Toggle Generator UI ---
def toggle_generator_ui():
    if generate_mode_var.get():
        gen_frame.grid(row=3, column=0, columnspan=4, pady=(10,15), sticky="ew")
    else:
        gen_frame.grid_remove()

# --- UI Setup ---
frame = ttk.Frame(root, padding=12)
frame.pack(fill=BOTH, expand=YES)

# Password Entry & Copy Button
ttk.Label(frame, text="Enter Password:").grid(row=0, column=0, sticky=W)
password_entry = ttk.Entry(frame, width=30, show="•")
password_entry.grid(row=0, column=1, sticky=W, padx=(5,0))
password_entry.bind("<KeyRelease>", check_password)

copy_button = ttk.Button(frame, text="⧉", width=3, command=copy_to_clipboard)
copy_button.grid(row=0, column=2, sticky=W, padx=(5,10))

show_password_check = ttk.Checkbutton(frame, text="Show Password", variable=show_password_var,
                                      command=toggle_password_visibility)
show_password_check.grid(row=0, column=3, sticky=W)

# Generate Password Checkbox
generate_check = ttk.Checkbutton(frame, text="Generate Password", variable=generate_mode_var,
                                 command=toggle_generator_ui)
generate_check.grid(row=1, column=0, columnspan=4, sticky=W, pady=(10,5))

# Generator UI Frame (hidden initially)
gen_frame = ttk.Frame(frame)
# gen_frame.grid(row=3, column=0, columnspan=4, pady=(10,15), sticky="ew")  # Start hidden - will grid when checkbox selected

ttk.Label(gen_frame, text="Mode:").grid(row=0, column=0, sticky=W)
mode_combo = ttk.Combobox(gen_frame, textvariable=mode_var, values=["Easy", "Medium", "Hard"], state="readonly", width=10)
mode_combo.grid(row=0, column=1, sticky=W, padx=(5,15))

ttk.Label(gen_frame, text="Length:").grid(row=0, column=2, sticky=W)
length_slider = ttk.Scale(
    gen_frame, 
    from_=6, 
    to=32, 
    variable=length_var, 
    orient=HORIZONTAL, 
    length=160, 
    command=lambda value: length_var.set(int(float(value)))  # Convert float to integer
)
length_slider.grid(row=0, column=3, sticky=W, padx=(5,10))
length_val_label = ttk.Label(gen_frame, textvariable=length_var, width=3)
length_val_label.grid(row=0, column=4, sticky=W)

generate_button = ttk.Button(gen_frame, text="Generate", command=perform_generate_password)
generate_button.grid(row=0, column=5, sticky=W)

# Result Label
result_label = ttk.Label(frame, text="")
result_label.grid(row=2, column=0, columnspan=4, pady=(5,10), sticky=W)

# --- Meter ---
meter_widget = ttk.Meter(frame, amountused=0, subtext="0% Strength", bootstyle="danger")
meter_widget.grid(row=4, column=0, columnspan=4, pady=(10,20), sticky="ew")

# --- Category Bars ---
cat_frame = ttk.Frame(frame)
cat_frame.grid(row=5, column=0, columnspan=4, sticky=W)

ttk.Label(cat_frame, text="Length:").grid(row=0, column=0, sticky=W)
length_bar = ttk.Progressbar(cat_frame, length=160, maximum=10, mode='determinate', bootstyle="secondary")
length_bar.grid(row=0, column=1, sticky=W, padx=(5,5))
length_score_label = ttk.Label(cat_frame, text="0", width=3)
length_score_label.grid(row=0, column=2, sticky=W)

ttk.Label(cat_frame, text="Variety:").grid(row=1, column=0, sticky=W)
variety_bar = ttk.Progressbar(cat_frame, length=160, maximum=10, mode='determinate', bootstyle="secondary")
variety_bar.grid(row=1, column=1, sticky=W, padx=(5,5))
variety_score_label = ttk.Label(cat_frame, text="0", width=3)
variety_score_label.grid(row=1, column=2, sticky=W)

ttk.Label(cat_frame, text="Entropy:").grid(row=2, column=0, sticky=W)
entropy_bar = ttk.Progressbar(cat_frame, length=160, maximum=10, mode='determinate', bootstyle="secondary")
entropy_bar.grid(row=2, column=1, sticky=W, padx=(5,5))
entropy_score_label = ttk.Label(cat_frame, text="0", width=3)
entropy_score_label.grid(row=2, column=2, sticky=W)

ttk.Label(cat_frame, text="Sequence Penalty:").grid(row=3, column=0, sticky=W)
sequence_bar = ttk.Progressbar(cat_frame, length=160, maximum=10, mode='determinate', bootstyle="secondary")
sequence_bar.grid(row=3, column=1, sticky=W, padx=(5,5))
sequence_score_label = ttk.Label(cat_frame, text="0", width=3)
sequence_score_label.grid(row=3, column=2, sticky=W)

# --- Help and About Buttons ---
help_button = ttk.Button(frame, text="Help", command=show_help)
help_button.grid(row=6, column=2, sticky=E, padx=5, pady=10)

about_button = ttk.Button(frame, text="About", command=show_about)
about_button.grid(row=6, column=3, sticky=E, padx=5, pady=10)

# --- Menu Bar ---
menubar = ttk.Menu(root)
root.option_add('*tearOff', False)
root.config(menu=menubar)

help_menu = ttk.Menu(menubar, tearoff=0)
help_menu.add_command(label="Help", command=show_help)
help_menu.add_command(label="About", command=show_about)
menubar.add_cascade(label="Help", menu=help_menu)

# --- Initialize ---
clear_category_scores()
root.mainloop()
