"""
Authentication Protocol - Hybrid Auth System
Combines AES (symmetric) & RSA (asymmetric) for secure challenge-response auth.
"""
import json
import os
import time
import hashlib
from dataclasses import dataclass, asdict
from typing import Optional

from .symmetric import AESManager
from .asymmetric import RSAManager, HybridEncryptor


@dataclass
class AuthToken:
    """Authentication token with metadata."""
    user_id: str
    issued_at: float
    expires_at: float
    signature: str  # RSA signature by issuer
    payload: dict = None

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    @staticmethod
    def from_json(data: str) -> 'AuthToken':
        return AuthToken(**json.loads(data))


class AuthServer:
    """
    Authentication Server (holder of RSA private key).
    Issues & verifies tokens, manages user credentials.
    """

    def __init__(self, server_id: str = "auth-server-01"):
        self.server_id = server_id
        self.private_key, self.public_key = RSAManager.generate_keypair()
        self.users_db = {}  # username -> hashed_password

        # Master AES key for internal session encryption
        self.master_aes_key = AESManager.generate_key()

    def register_user(self, username: str, password: str) -> bool:
        """Register a new user with hashed password."""
        if username in self.users_db:
            return False
        salt = os.urandom(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)
        self.users_db[username] = {
            'hash': pwd_hash,
            'salt': salt,
        }
        return True

    def authenticate(self, username: str, password: str) -> Optional[AuthToken]:
        """
        Authenticate user via password → issue signed AuthToken.

        Returns AuthToken if valid, None if invalid.
        """
        user = self.users_db.get(username)
        if not user:
            return None

        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), user['salt'], 100_000)
        if pwd_hash != user['hash']:
            return None

        token = AuthToken(
            user_id=username,
            issued_at=time.time(),
            expires_at=time.time() + 3600,  # 1 hour
            signature='',  # filled below
            payload={'role': 'user', 'server': self.server_id},
        )

        # Sign the token data with RSA
        token_data = f"{token.user_id}:{token.issued_at}:{token.expires_at}:{json.dumps(token.payload)}"
        token.signature = RSAManager.sign(token_data, self.private_key)
        return token

    def verify_token(self, token: AuthToken) -> bool:
        """Verify AuthToken RSA signature & expiry."""
        if token.is_expired():
            return False

        token_data = f"{token.user_id}:{token.issued_at}:{token.expires_at}:{json.dumps(token.payload)}"
        return RSAManager.verify(token_data, token.signature, self.public_key)

    def get_public_key_pem(self) -> bytes:
        """Export public key for clients."""
        return RSAManager.public_to_pem(self.public_key)

    def get_server_id(self) -> str:
        return self.server_id


class AuthClient:
    """
    Authentication Client (holds server's RSA public key).
    Authenticates to server, encrypts data with hybrid encryption.
    """

    def __init__(self, username: str, server_public_key_pem: bytes):
        self.username = username
        self.server_public_key = RSAManager.load_public_key(server_public_key_pem)
        self.current_token: Optional[AuthToken] = None

        # Client's own RSA keypair for signing requests
        self.private_key, self.public_key = RSAManager.generate_keypair()

    def login(self, server: AuthServer, password: str) -> bool:
        """Authenticate to server and store token."""
        token = server.authenticate(self.username, password)
        if token and server.verify_token(token):
            self.current_token = token
            return True
        return False

    def is_authenticated(self) -> bool:
        """Check if token exists and not expired."""
        return self.current_token is not None and not self.current_token.is_expired()

    def send_encrypted_message(self, message: str, server: AuthServer) -> dict:
        """
        Send an encrypted + signed message to the server.
        Uses hybrid encryption (RSA wraps AES).

        Args:
            message: Plaintext message
            server: AuthServer instance (for verification)

        Returns:
            Encrypted packet dict
        """
        if not self.is_authenticated():
            raise PermissionError("Not authenticated. Call login() first.")

        packet = {
            'user_id': self.username,
            'token': self.current_token.to_json(),
            'encrypted_data': HybridEncryptor.encrypt(message, server.public_key),
            'signature': RSAManager.sign(message, self.private_key),
            'client_public_key': RSAManager.public_to_pem(self.public_key).decode('utf-8'),
        }
        return packet

    @staticmethod
    def receive_encrypted_message(packet: dict, server: AuthServer) -> str:
        """
        Server receives & decrypts a client's encrypted message.

        Args:
            packet: Encrypted packet dict from send_encrypted_message()
            server: AuthServer instance

        Returns:
            Decrypted plaintext message, or raises on failure
        """
        # 1. Verify token
        token = AuthToken.from_json(packet['token'])
        if not server.verify_token(token):
            raise PermissionError("Invalid or expired token")

        # 2. Decrypt data using server's RSA private key
        plaintext = HybridEncryptor.decrypt(
            packet['encrypted_data'], server.private_key
        )

        # 3. Verify client signature
        client_public_key = RSAManager.load_public_key(
            packet['client_public_key'].encode('utf-8')
        )
        if not RSAManager.verify(plaintext, packet['signature'], client_public_key):
            raise PermissionError("Message signature verification failed")

        return plaintext

    def export_public_key(self) -> bytes:
        """Export client's RSA public key."""
        return RSAManager.public_to_pem(self.public_key)


class SecureChannel:
    """
    End-to-end encrypted channel using AES session key exchanged via RSA.
    Once session key is established, all traffic uses fast AES.
    """

    def __init__(self, owner_private_key, peer_public_key):
        self.owner_private_key = owner_private_key
        self.peer_public_key = peer_public_key
        self.session_key: Optional[bytes] = None

    def initiate(self) -> dict:
        """Generate & RSA-encrypt an AES session key for the peer."""
        self.session_key = AESManager.generate_key()
        encrypted_key = RSAManager.encrypt_aes_key(
            self.session_key, self.peer_public_key
        )
        return {'encrypted_session_key': encrypted_key}

    def accept(self, handshake: dict):
        """Decrypt AES session key from peer's handshake."""
        self.session_key = RSAManager.decrypt_aes_key(
            handshake['encrypted_session_key'], self.owner_private_key
        )

    def send(self, plaintext: str) -> dict:
        """Encrypt message with AES session key."""
        if not self.session_key:
            raise RuntimeError("Session not established")
        return AESManager.encrypt(plaintext, self.session_key)

    def receive(self, encrypted_data: dict) -> str:
        """Decrypt message with AES session key."""
        if not self.session_key:
            raise RuntimeError("Session not established")
        return AESManager.decrypt(encrypted_data, self.session_key)
