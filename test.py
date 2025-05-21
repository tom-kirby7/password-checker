import ttkbootstrap as ttk
from ttkbootstrap import Style
from tkinter import ttk
import math


style = Style()
style = Style('cosmo')
root = style.master
root.title("Tom Kirby's Password checker")
root.configure(background="black")
root.minsize(200, 200)
root.maxsize(1000, 1000)
root.geometry("600x600+100+100")

def length_score(password):
    length = len(password)
    if length == 0:
        print("Password is empty")
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
    else:
        return 0
    
def calculate_entropy(password):
    lowercase = any(c.islower() for c in password)
    uppercase = any(c.isupper() for c in password)
    digits = any(c.isdigit() for c in password)
    symbols = any(not c.isalnum() for c in password)

    escore = 0
    if lowercase:
        escore += 26
    if uppercase:
        escore += 26
    if digits:
        escore += 10
    if symbols:
        escore += 33

    if escore == 0 or len(password) == 0:   
        return 0
   
    entropy = len(password) * math.log2(escore)
    return entropy

def calculate_strength(password):
    length = length_score(password) * 0.2  # Weight: 20%
    variety = variety_score(password) * 0.4  # Weight: 40%
    entropy = calculate_entropy(password) * 0.3  # Weight: 30%
    pattern = repetition_and_pattern_score(password) * 0.1  # Weight: 10%

    total_strength = length + variety + entropy + pattern

    # Stricter thresholds for password categories
    if total_strength <= 10:
        return "Weak"
    elif total_strength <= 25:
        return "Moderate"
    elif total_strength <= 40:
        return "Strong"
    else:
        return "Very Strong"



# List of prohibited passwords
prohibited_passwords = ["123456", "password", "123456789", "qwerty", "abc123", "password1", "123123"]

def check_password():
    password = password_entry.get()
    strength = calculate_strength(password)
    result_label.config(text=f"Password Strength: {strength}")
    
def check_password():
    password = password_entry.get()

    # Check if password is in the prohibited list
    if password in prohibited_passwords:
        result_label.config(text="❌ This password is too common. Choose a different one.")
        return

    # Calculate strength if allowed
    strength = calculate_strength(password)
    result_label.config(text=f"✅ Password Strength: {strength}")



from collections import Counter

def repetition_and_pattern_score(password):
    if not password:
        return 0

    password_lower = password.lower()

    # ------------------------
    # 🔁 1. Repetition Check
    # ------------------------
    counts = Counter(password_lower)
    most_common = counts.most_common(1)[0][1]  # how many times the most common char appears

    length = len(password)
    repetition_ratio = most_common / length

    # The higher the repetition ratio, the lower the score
    if repetition_ratio >= 0.6:
        rep_score = 2
    elif repetition_ratio >= 0.4:
        rep_score = 4
    elif repetition_ratio >= 0.3:
        rep_score = 6
    elif repetition_ratio >= 0.2:
        rep_score = 8
    else:
        rep_score = 10

    # ------------------------
    # 🔢 2. Pattern Check
    # ------------------------
    common_patterns = [
        "1234", "2345", "3456", "4567", "5678", "6789",
        "abcd", "bcde", "cdef", "qwerty", "asdf", "zxcv",
        "password", "letmein", "admin", "iloveyou", "welcome"
    ]

    pattern_found = any(pat in password_lower for pat in common_patterns)

    if pattern_found:
        pat_score = 3  # big penalty
    else:
        pat_score = 10

    # ------------------------
    # ✅ Final Score
    # ------------------------
    # Use the lower of the two scores (bad repetition or bad pattern → bad password)
    final_score = min(rep_score, pat_score)
    return final_score





































def open_about_window():
    about_window = ttk.Toplevel(root)  # Create a new top-level window
    about_window.title("About")
    about_window.geometry("300x150")
    about_window.configure(background="black")

    # Add content to the About window
    about_label = ttk.Label(
        about_window,
        text="Password Checker v1.0\nCreated by Tom Kirby",
        font=("Segoe UI", 12),
        foreground="white",
        background="black"
    )
    about_label.pack(pady=20)

    close_button = ttk.Button(
        about_window,
        text="Close",
        command=about_window.destroy,
        style='danger.TButton'
    )
    close_button.pack(pady=10)


password_entry = ttk.Entry(root, show="*", width=30)
password_entry.pack(pady=5)

check_button = ttk.Button(root, text="Check Password", command=check_password, style='secondary.TButton')
check_button.pack(pady=5)

result_label = ttk.Label(root, text="Password Strength: ", font=("Segoe UI", 14),
foreground="white", background=root.cget("background"))
result_label.pack(pady=5)

window = style.master
ttk.Button(window, text="Help", style='secondary.TButton').pack(side='left', padx=5, pady=10)
ttk.Button(window, text="About", command=open_about_window,  style='success.Outline.TButton').pack(side='left', padx=5, pady=10)
window.mainloop()