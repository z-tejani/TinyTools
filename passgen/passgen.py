import secrets
import string
import argparse

def generate_password(length=16, use_numbers=True, use_symbols=True):
    chars = string.ascii_letters
    if use_numbers:
        chars += string.digits
    if use_symbols:
        chars += string.punctuation

    password = ''.join(secrets.choice(chars) for _ in range(length))
    return password

def main():
    parser = argparse.ArgumentParser(description="Generate a secure, random password.")
    parser.add_argument("--length", type=int, default=16, help="Length of the password (default: 16)")
    parser.add_argument("--no-numbers", action="store_true", help="Exclude numbers")
    parser.add_argument("--no-symbols", action="store_true", help="Exclude symbols")
    
    args = parser.parse_args()
    
    password = generate_password(
        length=args.length,
        use_numbers=not args.no_numbers,
        use_symbols=not args.no_symbols
    )
    
    print(password)

if __name__ == "__main__":
    main()
