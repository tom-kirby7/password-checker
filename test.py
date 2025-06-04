import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import math
import random
import string

root = ttk.Window(themename="superhero")
root.title("Tom Kirby's Password Checker")
root.geometry("720x500")
root.minsize(450, 350)

# --- Variables ---
mode_var = ttk.StringVar(value="Medium")
length_var = ttk.IntVar(value=12)
show_password_var = ttk.BooleanVar(value=False)
generate_mode_var = ttk.BooleanVar(value=False)
gen_visible = False

# --- Load prohibited passwords ---
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
    """Calculate the penalty for common sequences in the password."""
    common_seqs = ["123", "234", "345", "456", "567", "678", "789", "890",
                   "abc", "bcd", "cde", "def", "efg", "fgh", "ghi", "hij",
                   "qwe", "wer", "ert", "rty", "tyu", "yui", "uio", "iop",
                   "asd", "sdf", "dfg", "fgh", "ghj", "hjk", "jkl",
                   "zxc", "xcv", "cvb", "vbn", "bnm",
                   "password", "letmein", "admin", "welcome"]
    penalty = 0
    for seq in common_seqs:
        penalty += password.lower().count(seq) * 5  # Penalize for each occurrence of a sequence
    return penalty

def total_score(password):
    """Calculate the total score for the password."""
    length_score = score_length(password)
    variety_score = score_variety(password)
    entropy_score = score_entropy(password)
    seq_penalty = score_keyboard_sequence(password)

    base_score = length_score + variety_score + entropy_score
    total = base_score - seq_penalty
    return max(total, 0), length_score, variety_score, entropy_score, seq_penalty  # Ensure total is not negative

def strength_label(score):
    if score <= 9: return "Very Weak"
    elif score <= 15: return "Weak"
    elif score <= 21: return "Moderate"
    elif score <= 25.5: return "Strong"
    else: return "Very Strong"

def meter_bootstyle(score):
    """Determine the meter color based on the score."""
    if score <= 10:
        return "danger"  # Red
    elif score <= 20:
        return "warning"  # Yellow
    else:
        return "success"  # Green

def get_bootstyle(score, penalty=False):
    if penalty:
        return "danger"
    return meter_bootstyle(score)

# --- Password Generator ---
def perform_generate_password():
    mode = mode_var.get()
    length = length_var.get()

    if mode == "Easy":
        charset = string.ascii_lowercase
        min_types = 1
        min_score = 10
    elif mode == "Medium":
        charset = string.ascii_letters + string.digits
        min_types = 2
        min_score = 20
    else:
        charset = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
        min_types = 4
        min_score = 30

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

        score, *_ = total_score(password)
        if score >= min_score:
            password_entry.delete(0, 'end')
            password_entry.insert(0, password)
            check_password()
            return

    result_label.config(text="⚠️ Couldn't generate a password meeting the criteria. Try again.")

def strengthen_password(password):
    """Append characters to strengthen a password based on its weakest components."""
    if not password:
        return "❌ Please provide a password to strengthen."

    strengthened_password = password  # Start with the original password
    charset = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"

    # Analyze the current password's scores
    score, len_score, var_score, ent_score, seq_penalty = total_score(strengthened_password)

    # Improve variety by appending missing character types
    if var_score < 10:
        if not any(c.islower() for c in strengthened_password):
            strengthened_password += random.choice(string.ascii_lowercase)
        if not any(c.isupper() for c in strengthened_password):
            strengthened_password += random.choice(string.ascii_uppercase)
        if not any(c.isdigit() for c in strengthened_password):
            strengthened_password += random.choice(string.digits)
        if not any(not c.isalnum() for c in strengthened_password):
            strengthened_password += random.choice("!@#$%^&*()-_=+[]{}|;:,.<>?")

    # Improve entropy by appending random characters if needed
    if ent_score < 10:
        additional_entropy = ''.join(random.choices(charset, k=2))
        strengthened_password += additional_entropy

    # Ensure the password meets the minimum length
    min_length = 12  # Minimum recommended length for a strong password
    while len(strengthened_password) < min_length:
        strengthened_password += random.choice(charset)

    # Avoid known sequences by appending random characters if sequences are detected
    if any(seq in strengthened_password.lower() for seq in ["123", "abc", "password", "qwe"]):
        strengthened_password += random.choice("!@#$")

    # Return only the original password with appended characters
    return strengthened_password[:len(password)] + strengthened_password[len(password):]

def strengthen_password_to_strength(password, desired_strength):
    """Strengthen the password to the desired strength level."""
    if not password:
        return "❌ Please provide a password to strengthen."

    # Define relative thresholds for each strength level
    thresholds = {
        "Weak": 30,  # 30% strength
        "Moderate": 50,  # 50% strength
        "Strong": 75,  # 75% strength
        "Very Strong": 95  # 95% strength
    }

    target_percent = thresholds.get(desired_strength, 95)  # Default to "Very Strong"
    score, *_ = total_score(password)
    current_percent = (score / 30) * 100  # Convert score to percentage

    # Check if the password is already stronger than the desired mode
    if current_percent >= target_percent:
        return f"⚠️ Password is already stronger than {desired_strength}."

    strengthened_password = password
    attempts = 0

    while attempts < 50:  # Limit attempts to avoid infinite loops
        score, *_ = total_score(strengthened_password)
        current_percent = (score / 30) * 100  # Convert score to percentage
        if current_percent >= target_percent:
            break

        strengthened_password = strengthen_password(strengthened_password)
        attempts += 1

    return strengthened_password

def show_strengthen_options():
    """Show three password options after strengthening."""
    current_password = password_entry.get()
    if not current_password:
        result_label.config(text="❌ Please enter a password to strengthen.")
        return

    desired_strength = mode_var.get()
    options_window = ttk.Toplevel(root)
    options_window.title("Choose a Strengthened Password")
    options_window.geometry("400x250")

    ttk.Label(
        options_window, 
        text=f"Choose a password strengthened to {desired_strength}:", 
        font=("Segoe UI", 12)
    ).pack(pady=10)

    # Check if the password is already stronger than the desired mode
    result = strengthen_password_to_strength(current_password, desired_strength)
    if result.startswith("⚠️"):
        ttk.Label(
            options_window, 
            text=result, 
            font=("Segoe UI", 10), 
            foreground="red"
        ).pack(pady=10)
        ttk.Button(
            options_window, 
            text="Close", 
            command=options_window.destroy, 
            bootstyle="danger"
        ).pack(pady=10)
        return

    # Generate three unique options
    generated_passwords = set()
    while len(generated_passwords) < 3:
        strengthened_password = strengthen_password_to_strength(current_password, desired_strength)
        if not strengthened_password.startswith("⚠️"):
            generated_passwords.add(strengthened_password)

    for password in generated_passwords:
        ttk.Button(
            options_window, 
            text=password, 
            command=lambda pw=password: select_strengthened_password(pw, options_window), 
            bootstyle="primary"
        ).pack(pady=5)

def select_strengthened_password(password, window):
    """Select a strengthened password and populate it in the password checker."""
    password_entry.delete(0, 'end')
    password_entry.insert(0, password)
    window.destroy()
    check_password()

def show_strengthen_ui():
    """Show the UI for selecting strength and options after pressing 'Strengthen Password'."""
    global strengthen_ui_visible
    if not strengthen_ui_visible:
        strengthen_frame.grid(row=3, column=0, columnspan=4, pady=(10, 15), sticky="ew")
        strengthen_ui_visible = True
    else:
        strengthen_frame.grid_remove()
        strengthen_ui_visible = False

# --- UI Update Functions ---
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
    result_label.config(text=f"Password Strength: {label}{' (Penalty for sequence!)' if seq_penalty else ''}")
    update_meter(score, meter_bootstyle(score))
    update_category_scores(len_score, var_score, ent_score, seq_penalty)

def update_meter(score, style):
    """Update the meter widget with the score and corresponding style."""
    percent = (score / 30) * 100
    meter_widget.configure(amountused=percent, bootstyle=style, subtext=f"{percent:.0f}% Strength")

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

def toggle_password_visibility():
    password_entry.configure(show="" if show_password_var.get() else "•")

def copy_to_clipboard():
    password = password_entry.get()
    if password:
        root.clipboard_clear()
        root.clipboard_append(password)
        root.update()

def show_help():
    help_window = ttk.Toplevel(root)
    help_window.title("Help")
    help_window.geometry("400x200")
    ttk.Label(help_window, text=(
        "Enter a password to check its strength.\n"
        "Strength is based on length, variety, entropy, and penalties.\n\n"
        "Click 'Generate Password' to create a strong password."), justify="left").pack(padx=10, pady=10)
    ttk.Button(help_window, text="Close", command=help_window.destroy, bootstyle="primary").pack(pady=10)

def show_about():
    about_window = ttk.Toplevel(root)
    about_window.title("About")
    about_window.geometry("400x150")
    ttk.Label(about_window, text=(
        "Password Checker v1.0\n"
        "Created by Tom Kirby\n"
        "Evaluate or generate secure passwords."), justify="center").pack(padx=10, pady=10)
    ttk.Button(about_window, text="Close", command=about_window.destroy, bootstyle="primary").pack(pady=10)

def toggle_generator_ui():
    global gen_visible
    if not gen_visible:
        gen_frame.grid(row=3, column=0, columnspan=4, pady=(10, 15), sticky="ew")
    else:
        gen_frame.grid_remove()
    gen_visible = not gen_visible

# --- UI Layout ---
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

# Strengthen Password Button
strengthen_password_button = ttk.Button(
    frame,
    text="Strengthen Password",
    command=show_strengthen_ui,
    bootstyle="success"
)
strengthen_password_button.grid(row=2, column=0, columnspan=4, sticky=W, pady=(10, 5))

# Strengthen UI Frame (hidden initially)
strengthen_ui_visible = False
strengthen_frame = ttk.Frame(frame)
strengthen_frame.grid(row=3, column=0, columnspan=4, pady=(10, 15), sticky="ew")
strengthen_frame.grid_remove()

# Strengthen To Dropdown
ttk.Label(strengthen_frame, text="Strengthen To:", font=("Segoe UI", 12)).grid(row=1, column=0, sticky=W, padx=(5, 5))
strengthen_mode_combo = ttk.Combobox(
    strengthen_frame,
    textvariable=mode_var,
    values=["Weak", "Moderate", "Strong", "Very Strong"],
    state="readonly",
    width=12
)
strengthen_mode_combo.grid(row=1, column=1, sticky=W, padx=(5, 5))

# Strengthen Options Button
strengthen_options_button = ttk.Button(
    strengthen_frame,
    text="Strengthen Options",
    command=show_strengthen_options,
    bootstyle="primary"
)
strengthen_options_button.grid(row=1, column=2, sticky=W, padx=(5, 10))

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
    command=lambda value: length_var.set(int(float(value)))  # Ensure only integers are set
)
length_slider.grid(row=0, column=3, sticky=W, padx=(5,10))
length_val_label = ttk.Label(gen_frame, textvariable=length_var, width=3)
length_val_label.grid(row=0, column=4, sticky=W)

generate_button = ttk.Button(gen_frame, text="Generate", command=perform_generate_password)
generate_button.grid(row=0, column=5, sticky=W)

# Result Label
result_label = ttk.Label(frame, text="")
result_label.grid(row=4, column=0, columnspan=4, pady=(5,10), sticky=W)

# --- Meter ---
meter_widget = ttk.Meter(frame, amountused=0, subtext="0% Strength", bootstyle="danger")
meter_widget.grid(row=5, column=0, columnspan=4, pady=(10,20), sticky="ew")

# --- Category Bars ---
cat_frame = ttk.Frame(frame)
cat_frame.grid(row=6, column=0, columnspan=4, sticky=W)

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
help_button.grid(row=7, column=2, sticky=E, padx=5, pady=10)

about_button = ttk.Button(frame, text="About", command=show_about)
about_button.grid(row=7, column=3, sticky=E, padx=5, pady=10)

# --- Menu Bar ---
menubar = ttk.Menu(root)
root.option_add('*tearOff', False)
root.config(menu=menubar)

help_menu = ttk.Menu(menubar, tearoff=0)
help_menu.add_command(label="Help", command=show_help)
help_menu.add_command(label="About", command=show_about)
menubar.add_cascade(label="Help", menu=help_menu)

# --- Initialize ---
root.mainloop()