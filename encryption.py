from cryptography.fernet import Fernet

# generate key once and keep safe
key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_password(password):
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(password):
    return cipher.decrypt(password.encode()).decode()