def print_prohibited_passwords(filename):
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
            print("Prohibited Passwords:")
            for line in file:
                print(line.strip())
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")

# Example usage
print_prohibited_passwords('prohibited.txt')
