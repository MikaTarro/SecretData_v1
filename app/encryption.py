from cryptography.fernet import Fernet

# Генерация ключа для шифрования
encryption_key = Fernet.generate_key()
cipher = Fernet(encryption_key)
