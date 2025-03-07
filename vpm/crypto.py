import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CryptoHandler:
    def __init__(self, key=None):
        """Initialize with a shared key or generate one"""
        self.key = key if key else os.urandom(32)
        
    def generate_key_from_password(self, password, salt=None):
        """Generate a key from a password using PBKDF2"""
        if not salt:
            salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        self.key = kdf.derive(password.encode())
        return salt
        
    def encrypt(self, data):
        """Encrypt data with current key"""
        if isinstance(data, str):
            data = data.encode()
            
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        
        # Pad the data to be a multiple of 16 bytes (AES block size)
        pad_len = 16 - (len(data) % 16)
        padded_data = data + bytes([pad_len]) * pad_len
        
        ct = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(iv + ct).decode('utf-8')
        
    def decrypt(self, encrypted_data):
        """Decrypt data with current key"""
        raw_data = base64.b64decode(encrypted_data)
        iv, ct = raw_data[:16], raw_data[16:]
        
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        
        padded_data = decryptor.update(ct) + decryptor.finalize()
        pad_len = padded_data[-1]
        return padded_data[:-pad_len]
