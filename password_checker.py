import tkinter as tk
from tkinter import ttk
import math

root = tk.Tk()
root.title("Tom Kirby's Password checker")
root.configure(background="white")
root.minsize(400, 400)
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

tk.Label(root, text="Tom Kirby's Password Checker", font=("Arial", 16), bg="black", fg="white").pack(pady=10)
tk.Label(root, text="Enter your password:", bg="black", fg="white").pack(pady=5)

password_entry = tk.Entry(root, show="9", width=30)
password_entry.pack(pady=5)

check_button = tk.Button(root, text="Check Strength", bg="black", fg="black", command=check_password)
check_button.pack(pady=20)

about_button = tk.Button(root, text="About", command=lambda: result_label.config(text="Tom Kirby's Password Checker v1.0\nCreated by Tom Kirby"))
about_button.pack(pady=20)

result_label = tk.Label(root, text="", bg="black", fg="white", font=("Arial", 12))
result_label.pack(pady=20)

root.mainloop()


