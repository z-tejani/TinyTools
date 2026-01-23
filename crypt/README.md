# Crypt.py - The Tiny Vault

Secure symmetric file encryption using a password.

## Summary
`crypt.py` uses the `cryptography` library (Fernet/AES) to encrypt files. It derives a strong key from your password using PBKDF2 with a unique salt for every file.

## Installation
Requires Python 3 and the `cryptography` library.
```bash
pip install cryptography
```

## Usage
### Encrypt a file
```bash
python3 crypt.py encrypt my_data.txt
```
This creates `my_data.txt.enc`.

### Decrypt a file
```bash
python3 crypt.py decrypt my_data.txt.enc
```
This restores the original file.

**Warning:** There is no password recovery. If you lose the password, the data is gone.
