#!/usr/bin/env python3
"""
Crypt.py - The Tiny Vault
Simple symmetric file encryption using a password.

Usage:
    python3 crypt.py encrypt <file>
    python3 crypt.py decrypt <file>

Dependencies:
    pip install cryptography
"""

import sys
import os
import getpass
import base64

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:
    print("Error: Missing dependency 'cryptography'.")
    print("Please install it running: pip install cryptography")
    sys.exit(1)

def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 32-byte key from the password using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_file(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        return

    password = getpass.getpass("Enter password to encrypt: ")
    confirm = getpass.getpass("Confirm password: ")
    
    if password != confirm:
        print("Error: Passwords do not match.")
        return

    # Generate a random 16-byte salt
    salt = os.urandom(16)
    key = derive_key(password, salt)
    f = Fernet(key)

    with open(filepath, "rb") as file:
        file_data = file.read()

    encrypted_data = f.encrypt(file_data)

    # Output file: original.ext.enc
    out_path = filepath + ".enc"
    
    # Store salt as the first 16 bytes of the file
    with open(out_path, "wb") as file:
        file.write(salt)
        file.write(encrypted_data)

    print(f"[*] File encrypted successfully: {out_path}")
    print(f"[*] Note: Do not lose the password. There is no recovery.")
    
    # Optional: Ask to delete original
    # choice = input("Delete original file? (y/N): ")
    # if choice.lower() == 'y':
    #     os.remove(filepath)
    #     print("Original file deleted.")

def decrypt_file(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        return
        
    password = getpass.getpass("Enter password to decrypt: ")

    try:
        with open(filepath, "rb") as file:
            # Read the salt (first 16 bytes)
            salt = file.read(16)
            encrypted_data = file.read()

        key = derive_key(password, salt)
        f = Fernet(key)
        
        decrypted_data = f.decrypt(encrypted_data)

        # Determine output filename
        # Remove .enc if present
        if filepath.endswith(".enc"):
            out_path = filepath[:-4]
        else:
            out_path = filepath + ".decrypted"

        with open(out_path, "wb") as file:
            file.write(decrypted_data)

        print(f"[*] File decrypted successfully: {out_path}")

    except Exception as e:
        # Generic catch-all, but usually InvalidToken means wrong password
        print(f"Error: Decryption failed. Wrong password or corrupted file.")
        # print(e) # Uncomment for debug

def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    action = sys.argv[1]
    target = sys.argv[2]

    if action == "encrypt":
        encrypt_file(target)
    elif action == "decrypt":
        decrypt_file(target)
    else:
        print(f"Unknown command: {action}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
