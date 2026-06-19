"""
Asymmetric Encryption Module - RSA + AES Hybrid
Uses RSA to encrypt AES keys for secure key exchange + digital signatures.
"""
import os
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, utils
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

from .symmetric import AESManager


class RSAManager:
    """RSA-4096 asymmetric encryption & signing manager."""

    KEY_SIZE = 4096
    HASH_ALGO = hashes.SHA256()

    @staticmethod
    def generate_keypair() -> tuple:
        """
        Generate RSA-4096 keypair.

        Returns:
            (private_key, public_key) as cryptography objects
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=RSAManager.KEY_SIZE,
            backend=default_backend(),
        )
        public_key = private_key.public_key()
        return private_key, public_key

    @staticmethod
    def private_to_pem(private_key, password: str = None) -> bytes:
        """Serialize private key to PEM, optionally password-protected."""
        encryption = (
            serialization.BestAvailableEncryption(password.encode('utf-8'))
            if password else serialization.NoEncryption()
        )
        return private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption,
        )

    @staticmethod
    def public_to_pem(public_key) -> bytes:
        """Serialize public key to PEM."""
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    @staticmethod
    def load_private_key(pem_data: bytes, password: str = None) -> object:
        """Load private key from PEM bytes."""
        return serialization.load_pem_private_key(
            pem_data,
            password=password.encode('utf-8') if password else None,
            backend=default_backend(),
        )

    @staticmethod
    def load_public_key(pem_data: bytes) -> object:
        """Load public key from PEM bytes."""
        return serialization.load_pem_public_key(pem_data, backend=default_backend())

    @staticmethod
    def encrypt_aes_key(aes_key: bytes, public_key) -> str:
        """
        Encrypt an AES key using RSA-OAEP.

        Args:
            aes_key: AES key bytes (32 bytes)
            public_key: RSA public key

        Returns:
            Base64-encoded encrypted AES key
        """
        encrypted = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return base64.b64encode(encrypted).decode('utf-8')

    @staticmethod
    def decrypt_aes_key(encrypted_key_str: str, private_key) -> bytes:
        """
        Decrypt an RSA-OAEP encrypted AES key.

        Args:
            encrypted_key_str: Base64-encoded encrypted AES key
            private_key: RSA private key

        Returns:
            AES key bytes (32 bytes)
        """
        encrypted = base64.b64decode(encrypted_key_str.encode('utf-8'))
        return private_key.decrypt(
            encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    @staticmethod
    def sign(data: str, private_key) -> str:
        """
        Sign data with RSA private key (PKCS1v15 + SHA256).

        Args:
            data: String to sign
            private_key: RSA private key

        Returns:
            Base64-encoded signature
        """
        signature = private_key.sign(
            data.encode('utf-8'),
            padding.PKCS1v15(),
            RSAManager.HASH_ALGO,
        )
        return base64.b64encode(signature).decode('utf-8')

    @staticmethod
    def verify(data: str, signature_str: str, public_key) -> bool:
        """
        Verify RSA signature.

        Args:
            data: Original signed string
            signature_str: Base64-encoded signature
            public_key: RSA public key

        Returns:
            True if signature is valid, False otherwise
        """
        signature = base64.b64decode(signature_str.encode('utf-8'))
        try:
            public_key.verify(
                signature,
                data.encode('utf-8'),
                padding.PKCS1v15(),
                RSAManager.HASH_ALGO,
            )
            return True
        except InvalidSignature:
            return False


class HybridEncryptor:
    """
    Hybrid encryption: RSA encrypts AES key, AES encrypts data.
    Best of both worlds: security of RSA + speed of AES.
    """

    @staticmethod
    def encrypt(plaintext: str, public_key) -> dict:
        """
        Hybrid encrypt: generate AES key → encrypt data → RSA-encrypt AES key.

        Args:
            plaintext: String to encrypt
            public_key: RSA public key

        Returns:
            dict: {ciphertext, nonce, tag, encrypted_aes_key} all base64
        """
        aes_key = AESManager.generate_key()
        aes_result = AESManager.encrypt(plaintext, aes_key)
        encrypted_key = RSAManager.encrypt_aes_key(aes_key, public_key)

        return {
            **aes_result,
            'encrypted_aes_key': encrypted_key,
        }

    @staticmethod
    def decrypt(encrypted_data: dict, private_key) -> str:
        """
        Hybrid decrypt: RSA-decrypt AES key → AES-decrypt data.

        Args:
            encrypted_data: dict from encrypt()
            private_key: RSA private key

        Returns:
            Decrypted plaintext string
        """
        aes_key = RSAManager.decrypt_aes_key(
            encrypted_data['encrypted_aes_key'], private_key
        )
        return AESManager.decrypt(encrypted_data, aes_key)
