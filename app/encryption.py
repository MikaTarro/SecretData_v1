from cryptography.fernet import Fernet

# Генерация ключа для шифрования
encryption_key = Fernet.generate_key()  # Замените на постоянный ключ, если нужно
cipher = Fernet(encryption_key)
