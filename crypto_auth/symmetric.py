"""
Symmetric Encryption Module - AES
Uses AES-256-GCM for authenticated encryption with integrity verification.
"""
import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


class AESManager:
    """AES-256-GCM symmetric encryption manager."""

    KEY_SIZE = 32  # 256 bits
    NONCE_SIZE = 12  # 96 bits - recommended for GCM
    TAG_SIZE = 16  # 128 bits

    @staticmethod
    def generate_key() -> bytes:
        """Generate a cryptographically secure AES-256 key."""
        return os.urandom(AESManager.KEY_SIZE)

    @staticmethod
    def key_to_base64(key: bytes) -> str:
        """Encode key to base64 string for storage/transmission."""
        return base64.b64encode(key).decode('utf-8')

    @staticmethod
    def key_from_base64(key_str: str) -> bytes:
        """Decode key from base64 string."""
        return base64.b64decode(key_str.encode('utf-8'))

    @staticmethod
    def encrypt(plaintext: str, key: bytes) -> dict:
        """
        Encrypt plaintext using AES-256-GCM.

        Args:
            plaintext: String to encrypt
            key: AES key (32 bytes)

        Returns:
            dict with: ciphertext (base64), nonce (base64), tag (base64)
        """
        nonce = os.urandom(AESManager.NONCE_SIZE)
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()

        ciphertext = encryptor.update(plaintext.encode('utf-8')) + encryptor.finalize()
        tag = encryptor.tag

        return {
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'nonce': base64.b64encode(nonce).decode('utf-8'),
            'tag': base64.b64encode(tag).decode('utf-8'),
        }

    @staticmethod
    def decrypt(encrypted_data: dict, key: bytes) -> str:
        """
        Decrypt AES-256-GCM ciphertext.

        Args:
            encrypted_data: dict with ciphertext, nonce, tag (base64 strings)
            key: AES key (32 bytes)

        Returns:
            Decrypted plaintext string

        Raises:
            InvalidTag: if authentication fails (data tampered)
        """
        ciphertext = base64.b64decode(encrypted_data['ciphertext'])
        nonce = base64.b64decode(encrypted_data['nonce'])
        tag = base64.b64decode(encrypted_data['tag'])

        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()

        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext.decode('utf-8')

    @staticmethod
    def encrypt_file(filepath: str, key: bytes, output_path: str = None) -> str:
        """
        Encrypt a file using AES-256-GCM.

        Args:
            filepath: Path to input file
            key: AES key (32 bytes)
            output_path: Optional output path (default: filepath + '.enc')

        Returns:
            Path to encrypted file
        """
        if output_path is None:
            output_path = filepath + '.enc'

        with open(filepath, 'rb') as f:
            data = f.read()

        nonce = os.urandom(AESManager.NONCE_SIZE)
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        tag = encryptor.tag

        with open(output_path, 'wb') as f:
            f.write(nonce + tag + ciphertext)

        return output_path

    @staticmethod
    def decrypt_file(filepath: str, key: bytes, output_path: str = None) -> str:
        """
        Decrypt an AES-256-GCM encrypted file.

        Args:
            filepath: Path to encrypted file
            key: AES key (32 bytes)
            output_path: Optional output path (default: strip '.enc' or add '.dec')

        Returns:
            Path to decrypted file
        """
        if output_path is None:
            output_path = filepath.replace('.enc', '.dec') if filepath.endswith('.enc') else filepath + '.dec'

        with open(filepath, 'rb') as f:
            nonce = f.read(AESManager.NONCE_SIZE)
            tag = f.read(AESManager.TAG_SIZE)
            ciphertext = f.read()

        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        data = decryptor.update(ciphertext) + decryptor.finalize()

        with open(output_path, 'wb') as f:
            f.write(data)

        return output_path
