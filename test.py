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

def check_password():
    password = password_entry.get()
    strength = calculate_strength(password)
    result_label.config(text=f"Password Strength: {strength}")


password_entry = ttk.Entry(root, show="9", width=30)
password_entry.pack(pady=5)

check_button = ttk.Button(root, text="Check Password", command=check_password, style='secondary.TButton')
check_button.pack(pady=5)

result_label = ttk.Label(root, text="Password Strength: ", font=("Segoe UI", 14),
foreground="white", background=root.cget("background"))
result_label.pack(pady=5)

window = style.master
ttk.Button(window, text="Help", style='secondary.TButton').pack(side='left', padx=5, pady=10)
ttk.Button(window, text="About", style='success.Outline.TButton').pack(side='left', padx=5, pady=10)
window.mainloop()