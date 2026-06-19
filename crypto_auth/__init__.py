"""
CryptoAuth - Hybrid Authentication System
Combines AES (symmetric) & RSA (asymmetric) cryptography for secure authentication.
"""

__version__ = "1.0.0"

# Export symmetric encryption classes
from .symmetric import AESManager

# Export asymmetric encryption classes
from .asymmetric import RSAManager, HybridEncryptor

# Export authentication protocol classes
from .auth_protocol import (
    AuthToken,
    AuthServer,
    AuthClient,
    SecureChannel,
)

__all__ = [
    # Symmetric
    'AESManager',
    
    # Asymmetric
    'RSAManager',
    'HybridEncryptor',
    
    # Authentication
    'AuthToken',
    'AuthServer',
    'AuthClient',
    'SecureChannel',
]
