import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import math
import random
import string

root = ttk.Window(themename="journal")
root.title("Tom Kirby's Password Checker")
root.geometry("650x450")
root.minsize(450, 350)

# --- Style for sequence bar coloring ---
style = ttk.Style()
style.configure("green.Horizontal.TProgressbar", troughcolor="white", background="green")
style.configure("danger.Horizontal.TProgressbar", troughcolor="white", background="red")

# --- Variables ---
mode_var = ttk.StringVar(value="Medium")  # Password generation mode
length_var = ttk.IntVar(value=12)         # Password length

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
    # Returns penalty magnitude (positive number) if sequences found
    common_seqs = ["123", "234", "345", "abc", "qwe", "asd", "password"]
    for seq in common_seqs:
        if seq in password.lower():
            return 5  # Penalty magnitude
    return 0  # No penalty

def total_score(password):
    len_s = score_length(password)
    var_s = score_variety(password)
    ent_s = score_entropy(password)
    seq_penalty = score_keyboard_sequence(password)

    # Total score = positive factors - penalty, weighted
    return (len_s * 0.3 + var_s * 0.3 + ent_s * 0.3) - (seq_penalty * 0.1)

def strength_label(score):
    if score <= 3: return "Very Weak"
    elif score <= 5: return "Weak"
    elif score <= 7: return "Moderate"
    elif score <= 8.5: return "Strong"
    else: return "Very Strong"

# --- Password Generator ---
def perform_generate_password():
    mode = mode_var.get()
    length = length_var.get()

    if mode == "Easy":
        charset = string.ascii_lowercase
        min_types = 1
        min_score = 2.5
    elif mode == "Medium":
        charset = string.ascii_letters + string.digits
        min_types = 2
        min_score = 5.5
    else:  # Hard
        charset = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
        min_types = 4
        min_score = 7.5

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
        clear_category_scores()
        return

    if password in prohibited_passwords:
        result_label.config(text="❌ This password is too common or not allowed.")
        update_meter(0)
        clear_category_scores()
        return

    len_score = score_length(password)
    var_score = score_variety(password)
    ent_score = score_entropy(password)
    seq_penalty = score_keyboard_sequence(password)

    score = total_score(password)
    label = strength_label(score)
    result_label.config(text=f"Password Strength: {label}")
    update_meter(min(max(score * 10, 0), 100))

    update_category_scores(len_score, var_score, ent_score, seq_penalty)

def clear_category_scores():
    for bar in [length_bar, variety_bar, entropy_bar, sequence_bar]:
        bar.configure(value=0, style="green.Horizontal.TProgressbar")
    for label in [length_score_label, variety_score_label, entropy_score_label, sequence_score_label]:
        label.config(text="0")

def update_category_scores(len_score, var_score, ent_score, seq_penalty):
    length_bar.configure(value=len_score)
    variety_bar.configure(value=var_score)
    entropy_bar.configure(value=ent_score)

    # Show penalty magnitude on sequence bar
    sequence_bar.configure(value=seq_penalty)
    if seq_penalty == 0:
        sequence_bar.configure(style="green.Horizontal.TProgressbar")
    else:
        sequence_bar.configure(style="danger.Horizontal.TProgressbar")

    length_score_label.config(text=f"{int(len_score)}/10")
    variety_score_label.config(text=f"{int(var_score)}/10")
    entropy_score_label.config(text=f"{int(ent_score)}/10")
    sequence_score_label.config(text=f"{int(seq_penalty)}/10 (Penalty)")

def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(password_entry.get())
    root.update()

def toggle_password_visibility():
    password_entry.configure(show="" if show_password_var.get() else "•")

# --- UI Layout ---
frame = ttk.Frame(root, padding=10)
frame.pack(expand=True, fill=BOTH)

# Password Entry
ttk.Label(frame, text="Password:").grid(row=0, column=0, sticky=W, padx=(0,5))
password_entry = ttk.Entry(frame, width=40, show="•")
password_entry.grid(row=0, column=1, sticky=EW)
password_entry.bind("<KeyRelease>", lambda e: check_password())

show_password_var = ttk.BooleanVar(value=False)
show_password_cb = ttk.Checkbutton(frame, text="Show Password", variable=show_password_var, command=toggle_password_visibility)
show_password_cb.grid(row=0, column=2, sticky=W, padx=10)

generate_button = ttk.Button(frame, text="Generate Password", command=perform_generate_password)
generate_button.grid(row=0, column=3, padx=10)

ttk.Label(frame, text="Mode:").grid(row=1, column=0, sticky=W, pady=(10,0))
mode_options = ttk.Combobox(frame, textvariable=mode_var, values=["Easy", "Medium", "Hard"], state="readonly", width=10)
mode_options.grid(row=1, column=1, sticky=W, pady=(10,0))

ttk.Label(frame, text="Length:").grid(row=1, column=2, sticky=E, pady=(10,0))
length_spinbox = ttk.Spinbox(frame, from_=6, to=32, textvariable=length_var, width=5)
length_spinbox.grid(row=1, column=3, sticky=W, pady=(10,0))

result_label = ttk.Label(frame, text="Enter a password to check strength.")
result_label.grid(row=2, column=0, columnspan=4, sticky=W, pady=(10,0))

meter_widget = ttk.Meter(frame, length=300, amountused=0, subtext="0% Strength", bootstyle="success")
meter_widget.grid(row=3, column=0, columnspan=4, pady=10)

cat_frame = ttk.LabelFrame(frame, text="Category Scores (0-10 scale)", padding=10)
cat_frame.grid(row=4, column=0, columnspan=4, sticky=EW, pady=(10,0))

ttk.Label(cat_frame, text="Length:").grid(row=0, column=0, sticky=W)
length_bar = ttk.Progressbar(cat_frame, length=150, maximum=10, mode='determinate', style="green.Horizontal.TProgressbar")
length_bar.grid(row=0, column=1, sticky=W, padx=(5,5))
length_score_label = ttk.Label(cat_frame, text="0")
length_score_label.grid(row=0, column=2, sticky=W)

ttk.Label(cat_frame, text="Variety:").grid(row=1, column=0, sticky=W)
variety_bar = ttk.Progressbar(cat_frame, length=150, maximum=10, mode='determinate', style="green.Horizontal.TProgressbar")
variety_bar.grid(row=1, column=1, sticky=W, padx=(5,5))
variety_score_label = ttk.Label(cat_frame, text="0")
variety_score_label.grid(row=1, column=2, sticky=W)

ttk.Label(cat_frame, text="Entropy:").grid(row=2, column=0, sticky=W)
entropy_bar = ttk.Progressbar(cat_frame, length=150, maximum=10, mode='determinate', style="green.Horizontal.TProgressbar")
entropy_bar.grid(row=2, column=1, sticky=W, padx=(5,5))
entropy_score_label = ttk.Label(cat_frame, text="0")
entropy_score_label.grid(row=2, column=2, sticky=W)

ttk.Label(cat_frame, text="Keyboard Sequence:").grid(row=3, column=0, sticky=W)
sequence_bar = ttk.Progressbar(cat_frame, length=150, maximum=10, mode='determinate', style="green.Horizontal.TProgressbar")
sequence_bar.grid(row=3, column=1, sticky=W, padx=(5,5))
sequence_score_label = ttk.Label(cat_frame, text="0")
sequence_score_label.grid(row=3, column=2, sticky=W)

frame.columnconfigure(1, weight=1)
cat_frame.columnconfigure(1, weight=1)

root.mainloop()
