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
    seq_penalty = score_keyboard_sequence(password)

    base_score = length_score + variety_score
    total = base_score - seq_penalty
    return max(total, 0), length_score, variety_score, seq_penalty  # Ensure total is not negative

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
    """Generate a password based on the selected mode and length."""
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
    else:  # Hard mode
        charset = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
        min_types = 4
        min_score = 30

    attempts = 0
    while attempts < 100:
        attempts += 1
        password_chars = []

        # Ensure minimum character type requirements
        if mode == "Easy":
            password_chars += random.choices(string.ascii_lowercase, k=length)
        elif mode == "Medium":
            password_chars += random.choices(string.ascii_lowercase, k=max(1, length // 3))
            password_chars += random.choices(string.ascii_uppercase, k=max(1, length // 4))
            password_chars += random.choices(string.digits, k=max(1, length // 4))
        else:  # Hard mode
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

        # Check if the password meets criteria
        if password in prohibited_passwords:
            continue
        if any(seq in password.lower() for seq in ["123", "abc", "password", "qwe"]):
            continue

        types_used = sum([
            any(c.islower() for c in password),
            any(c.isupper() for c in password),
            any(c.isdigit() for c in password),
            any(not c.isalnum() for c in password),
        ])
        if types_used < min_types:
            continue

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
    score, len_score, var_score, seq_penalty = total_score(strengthened_password)

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

    # Ensure the password meets the minimum length
    min_length = 12  # Minimum recommended length for a strong password
    while len(strengthened_password) < min_length:
        strengthened_password += random.choice(charset)

    # Avoid known sequences by appending random characters if sequences are detected
    if any(seq in strengthened_password.lower() for seq in ["123", "abc", "password", "qwe"]):
        strengthened_password += random.choice("!@#$")

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
    score, len_score, var_score, seq_penalty = total_score(password)
    current_percent = (score / 30) * 100  # Convert score to percentage

    # Check if the password is already stronger than the desired mode
    if current_percent >= target_percent:
        return f"⚠️ Password is already stronger than {desired_strength}."

    strengthened_password = password
    attempts = 0

    while attempts < 50:  # Limit attempts to avoid infinite loops
        score, len_score, var_score, seq_penalty = total_score(strengthened_password)
        current_percent = (score / 30) * 100  # Convert score to percentage

        if current_percent >= target_percent:
            break

        # Append characters based on missing components
        if var_score < 10:
            if not any(c.islower() for c in strengthened_password):
                strengthened_password += random.choice(string.ascii_lowercase)
            if not any(c.isupper() for c in strengthened_password):
                strengthened_password += random.choice(string.ascii_uppercase)
            if not any(c.isdigit() for c in strengthened_password):
                strengthened_password += random.choice(string.digits)
            if not any(not c.isalnum() for c in strengthened_password):
                strengthened_password += random.choice("!@#$%^&*()-_=+[]{}|;:,.<>?")

        # Ensure the password meets the minimum length relative to the target strength
        min_length = 8 if target_percent <= 50 else 12  # Moderate and below: 8, Strong and above: 12
        while len(strengthened_password) < min_length:
            strengthened_password += random.choice(string.ascii_letters + string.digits)

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
    options_window.geometry("500x300")  # Adjusted window size to fit all GUI elements

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

    score, len_score, var_score, seq_penalty = total_score(password)
    label = strength_label(score)
    result_label.config(text=f"Password Strength: {label}{' (Penalty for sequence!)' if seq_penalty else ''}")
    update_meter(score, meter_bootstyle(score))
    update_category_scores(len_score, var_score, seq_penalty)

def update_meter(score, style):
    """Update the meter widget with the score and corresponding style."""
    percent = (score / 30) * 100
    meter_widget.configure(amountused=percent, bootstyle=style, subtext=f"{percent:.0f}% Strength")

def clear_category_scores():
    for bar, label in [(length_bar, length_score_label), 
                       (variety_bar, variety_score_label), 
                       (sequence_bar, sequence_score_label)]:
        bar.configure(value=0, bootstyle="secondary")
        label.config(text="0")

def update_category_scores(len_score, var_score, seq_penalty):
    """Update the UI for category scores with distinct colors."""
    # Update length and variety with light blue
    length_bar.configure(value=len_score, bootstyle="info")
    variety_bar.configure(value=var_score, bootstyle="info")

    # Update sequence penalty with red
    sequence_bar.configure(value=seq_penalty, bootstyle="danger")

    # Update labels
    length_score_label.config(text=f"{int(len_score)}")
    variety_score_label.config(text=f"{int(var_score)}")
    sequence_score_label.config(text=f"-{int(seq_penalty)}" if seq_penalty else "0")

def toggle_password_visibility():
    password_entry.configure(show="" if show_password_var.get() else "•")

def copy_to_clipboard():
    password = password_entry.get()
    if password:
        root.clipboard_clear()
def show_help():
    """Display the Help window with categorized dropdowns and scrollable content."""
    help_window = ttk.Toplevel(root)
    help_window.title("Help")
    help_window.geometry("460x300")

    # Create a scrollable frame
    canvas = ttk.Canvas(help_window)
    scrollbar = ttk.Scrollbar(help_window, orient=VERTICAL, command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=LEFT, fill=BOTH, expand=YES)
    scrollbar.pack(side=RIGHT, fill=Y)

    # Section 1: How to Use
    how_to_use = ttk.Labelframe(scrollable_frame, text="🔍 HOW TO USE", padding=10)
    how_to_use.pack(fill=X, expand=YES, pady=5)
    ttk.Label(how_to_use, text=(
        "Enter a password in the text field to check its strength.\n"
        "Password strength is evaluated based on:\n"
        "- Length\n"
        "- Variety of characters (lowercase, uppercase, digits, symbols)\n"
        "- Penalties for common sequences or weak patterns."
    ), justify="left", wraplength=440).pack()

    # Section 2: Features
    features = ttk.Labelframe(scrollable_frame, text="🛠 FEATURES", padding=10)
    features.pack(fill=X, expand=YES, pady=5)
    ttk.Label(features, text=(
        "- 'Generate Password': Creates a secure password based on difficulty.\n"
        "- 'Strengthen Password': Improves your entered password.\n"
        "- Visual meter: Shows strength from red (weak) to green (strong).\n"
        "- Detailed score breakdown: Length, Variety, and Penalties."
    ), justify="left", wraplength=440).pack()

    # Section 3: Tips
    tips = ttk.Labelframe(scrollable_frame, text="🔒 TIPS", padding=10)
    tips.pack(fill=X, expand=YES, pady=5)
    ttk.Label(tips, text=(
        "- Avoid common words like 'password' or '123'.\n"
        "- Use symbols, numbers, and mix cases.\n"
        "- Aim for at least 12 characters."
    ), justify="left", wraplength=440).pack()

    ttk.Button(scrollable_frame, text="Close", command=help_window.destroy, bootstyle="primary").pack(pady=10)

def show_about():
    """Display the About window with categorized dropdowns and scrollable content."""
    about_window = ttk.Toplevel(root)
    about_window.title("About")
    about_window.geometry("460x300")

    # Create a scrollable frame
    canvas = ttk.Canvas(about_window)
    scrollbar = ttk.Scrollbar(about_window, orient=VERTICAL, command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=LEFT, fill=BOTH, expand=YES)
    scrollbar.pack(side=RIGHT, fill=Y)

    # Section 1: Application Info
    app_info = ttk.Labelframe(scrollable_frame, text="🔐 APPLICATION INFO", padding=10)
    app_info.pack(fill=X, expand=YES, pady=5)
    ttk.Label(app_info, text=(
        "This application helps users evaluate and strengthen passwords.\n\n"
        "📦 Version: 1.0\n"
        "👨‍💻 Developer: Tom Kirby"
    ), justify="left", wraplength=440).pack()

    # Section 2: Technology
    technology = ttk.Labelframe(scrollable_frame, text="📘 TECHNOLOGY", padding=10)
    technology.pack(fill=X, expand=YES, pady=5)
    ttk.Label(technology, text=(
        "- Built using Python and the ttkbootstrap GUI library.\n"
        "- Evaluates password strength using:\n"
        "   • Length score (up to 10 points)\n"
        "   • Variety score (lower/upper/digit/symbol)\n"
        "   • Sequence penalty (e.g., '123', 'abc', common passwords)."
    ), justify="left", wraplength=440).pack()

    # Section 3: Disclaimer
    disclaimer = ttk.Labelframe(scrollable_frame, text="📝 DISCLAIMER", padding=10)
    disclaimer.pack(fill=X, expand=YES, pady=5)
    ttk.Label(disclaimer, text=(
        "This tool is for educational purposes. For secure applications,\n"
        "use industry-standard password managers and hashing methods."
    ), justify="left", wraplength=440).pack()

    ttk.Button(scrollable_frame, text="Close", command=about_window.destroy, bootstyle="primary").pack(pady=10)

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

ttk.Label(cat_frame, text="Sequence Penalty:").grid(row=2, column=0, sticky=W)
sequence_bar = ttk.Progressbar(cat_frame, length=160, maximum=10, mode='determinate', bootstyle="secondary")
sequence_bar.grid(row=2, column=1, sticky=W, padx=(5,5))
sequence_score_label = ttk.Label(cat_frame, text="0", width=3)
sequence_score_label.grid(row=2, column=2, sticky=W)

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