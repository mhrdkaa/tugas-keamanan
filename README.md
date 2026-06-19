# CryptoAuth - Hybrid Authentication System

Sistem autentikasi lengkap yang menggabungkan **AES-256-GCM (symmetric)** dan **RSA-4096 (asymmetric)** untuk keamanan maksimal.

## 🔐 Fitur Utama

- **AES-256-GCM**: Enkripsi symmetric cepat dengan authenticated encryption (integrity check)
- **RSA-4096**: Enkripsi asymmetric + digital signatures untuk key exchange
- **Hybrid Encryption**: Kombinasi RSA + AES untuk performa dan keamanan optimal
- **Authentication Protocol**: Login berbasis token dengan RSA signature
- **Secure Channel**: Session key exchange via RSA untuk komunikasi cepat
- **File Encryption**: Enkripsi/dekripsi file dengan AES-256-GCM

## 📦 Instalasi

```bash
pip install cryptography
```

## 🚀 Quick Start

### 1. Enkripsi Symmetric (AES-256-GCM)

```python
from crypto_auth import AESManager

# Generate key
key = AESManager.generate_key()

# Encrypt
encrypted = AESManager.encrypt("Pesan rahasia", key)
print(f"Ciphertext: {encrypted['ciphertext']}")

# Decrypt
plaintext = AESManager.decrypt(encrypted, key)
print(f"Decrypted: {plaintext}")
```

### 2. Digital Signature (RSA-4096)

```python
from crypto_auth import RSAManager

# Generate keypair
private_key, public_key = RSAManager.generate_keypair()

# Sign message
message = "Dokumen penting"
signature = RSAManager.sign(message, private_key)

# Verify signature
is_valid = RSAManager.verify(message, signature, public_key)
print(f"Valid: {is_valid}")  # True
```

### 3. Hybrid Encryption (RSA + AES)

```python
from crypto_auth import HybridEncryptor, RSAManager

# Generate keypair
private_key, public_key = RSAManager.generate_keypair()

# Encrypt dengan public key (hanya private key bisa decrypt)
encrypted = HybridEncryptor.encrypt("Data sensitif", public_key)

# Decrypt dengan private key
plaintext = HybridEncryptor.decrypt(encrypted, private_key)
```

### 4. Authentication Protocol (Login + Token)

```python
from crypto_auth import AuthServer, AuthClient

# Setup server
server = AuthServer("my-server")
server.register_user("alice", "password123")

# Client login
client = AuthClient("alice", server.get_public_key_pem())
login_success = client.login(server, "password123")

if login_success:
    # Send encrypted message
    packet = client.send_encrypted_message("Hello Server!", server)
    
    # Server decrypt message
    received = AuthClient.receive_encrypted_message(packet, server)
    print(f"Server received: {received}")
```

### 5. Secure Channel (Session Key Exchange)

```python
from crypto_auth import SecureChannel, RSAManager

# Alice & Bob generate keypairs
alice_priv, alice_pub = RSAManager.generate_keypair()
bob_priv, bob_pub = RSAManager.generate_keypair()

# Establish secure channel
alice_channel = SecureChannel(alice_priv, bob_pub)
bob_channel = SecureChannel(bob_priv, alice_pub)

# Handshake
handshake = alice_channel.initiate()
bob_channel.accept(handshake)

# Fast encrypted communication
encrypted = alice_channel.send("Hi Bob!")
message = bob_channel.receive(encrypted)
```

### 6. File Encryption

```python
from crypto_auth import AESManager

key = AESManager.generate_key()

# Encrypt file
AESManager.encrypt_file("document.pdf", key, "document.pdf.enc")

# Decrypt file
AESManager.decrypt_file("document.pdf.enc", key, "document.pdf")
```

## 📁 Struktur Project

```
project-baru/
├── crypto_auth/
│   ├── __init__.py           # Package exports
│   ├── symmetric.py          # AES-256-GCM encryption
│   ├── asymmetric.py         # RSA-4096 + hybrid encryption
│   └── auth_protocol.py      # Authentication protocol
├── demo.py                   # Comprehensive demo (6 scenarios)
├── README.md                 # Documentation (this file)
└── requirements.txt          # Dependencies
```

## 🔒 Keamanan

### Algoritma yang Digunakan

| Komponen | Algoritma | Key Size | Mode/Padding |
|----------|-----------|----------|--------------|
| Symmetric | AES | 256-bit | GCM (authenticated) |
| Asymmetric | RSA | 4096-bit | OAEP (encryption) |
| Signature | RSA | 4096-bit | PKCS1v15 + SHA-256 |
| KDF | PBKDF2 | - | 100,000 iterations |

### Fitur Keamanan

✅ **Authenticated Encryption**: AES-GCM mencegah tampering (integrity check via tag)  
✅ **Perfect Forward Secrecy**: Setiap session menggunakan key berbeda  
✅ **Digital Signatures**: Verifikasi identitas pengirim dengan RSA  
✅ **Password Hashing**: PBKDF2-HMAC-SHA256 untuk password storage  
✅ **Token Expiry**: Auth token otomatis expire setelah 1 jam  
✅ **Hybrid Encryption**: Keamanan RSA + kecepatan AES  

## 🎯 Use Cases

### 1. Secure File Storage
Enkripsi file sebelum upload ke cloud storage.

### 2. End-to-End Messaging
Chat app dengan enkripsi end-to-end seperti WhatsApp.

### 3. API Authentication
Backend API dengan token-based authentication + encrypted payload.

### 4. Document Signing
Digital signature untuk dokumen legal/kontrak.

### 5. Key Exchange
Secure key exchange untuk establish encrypted session.

## 📚 API Reference

### AESManager

```python
# Generate key
key = AESManager.generate_key() -> bytes

# Key encoding
key_str = AESManager.key_to_base64(key) -> str
key = AESManager.key_from_base64(key_str) -> bytes

# Encrypt/Decrypt
encrypted = AESManager.encrypt(plaintext: str, key: bytes) -> dict
plaintext = AESManager.decrypt(encrypted_data: dict, key: bytes) -> str

# File operations
AESManager.encrypt_file(filepath: str, key: bytes, output_path: str = None)
AESManager.decrypt_file(filepath: str, key: bytes, output_path: str = None)
```

### RSAManager

```python
# Generate keypair
private_key, public_key = RSAManager.generate_keypair() -> tuple

# Serialize keys
pem = RSAManager.private_to_pem(private_key, password: str = None) -> bytes
pem = RSAManager.public_to_pem(public_key) -> bytes

# Load keys
private_key = RSAManager.load_private_key(pem_data: bytes, password: str = None)
public_key = RSAManager.load_public_key(pem_data: bytes)

# Encrypt/Decrypt AES key
encrypted = RSAManager.encrypt_aes_key(aes_key: bytes, public_key) -> str
aes_key = RSAManager.decrypt_aes_key(encrypted_key_str: str, private_key) -> bytes

# Sign/Verify
signature = RSAManager.sign(data: str, private_key) -> str
is_valid = RSAManager.verify(data: str, signature_str: str, public_key) -> bool
```

### HybridEncryptor

```python
# Encrypt with public key, decrypt with private key
encrypted = HybridEncryptor.encrypt(plaintext: str, public_key) -> dict
plaintext = HybridEncryptor.decrypt(encrypted_data: dict, private_key) -> str
```

### AuthServer

```python
server = AuthServer(server_id: str = "auth-server-01")
server.register_user(username: str, password: str) -> bool
token = server.authenticate(username: str, password: str) -> AuthToken | None
is_valid = server.verify_token(token: AuthToken) -> bool
public_key_pem = server.get_public_key_pem() -> bytes
```

### AuthClient

```python
client = AuthClient(username: str, server_public_key_pem: bytes)
success = client.login(server: AuthServer, password: str) -> bool
is_auth = client.is_authenticated() -> bool
packet = client.send_encrypted_message(message: str, server: AuthServer) -> dict

# Static method untuk server
message = AuthClient.receive_encrypted_message(packet: dict, server: AuthServer) -> str
```

### SecureChannel

```python
channel = SecureChannel(owner_private_key, peer_public_key)

# Initiator
handshake = channel.initiate() -> dict

# Acceptor
channel.accept(handshake: dict)

# Communication
encrypted = channel.send(plaintext: str) -> dict
plaintext = channel.receive(encrypted_data: dict) -> str
```

## 🧪 Testing

Jalankan demo lengkap (6 scenarios):

```bash
python demo.py
```

Output:
```
======================================================================
  DEMO 1: AES-256-GCM SYMMETRIC ENCRYPTION
======================================================================
[KEY] AES Key (base64): hC98oJk2y1kiNbuR3VtD40ukY8beztDDlA4HrBjRFMo=
[IN] Plaintext: Ini adalah pesan rahasia...
[ENC] Ciphertext: 4dQVG5Zdb/q6ZYWFVitz9iRvR41Ce1xbULozafgeG1i0...
[DEC] Decrypted: Ini adalah pesan rahasia...
[OK]  Match: True
[TEST] Tamper Detection: PASS: Detected tampering -> InvalidTag
```

## ⚠️ Important Notes

1. **Key Management**: Simpan private keys dengan aman. Jangan commit ke git!
2. **Password Protection**: Gunakan `RSAManager.private_to_pem(key, password="...")` untuk encrypt private key.
3. **Token Expiry**: Default token expire 1 jam. Adjust di `AuthServer.authenticate()`.
4. **Production Ready**: Tambahkan rate limiting, secure key storage (HSM/KMS), dan audit logging untuk production.

## 📝 License

Educational/Demo purposes. Silakan modifikasi sesuai kebutuhan.

## 🤝 Contributing

Feel free to improve! Beberapa improvement ideas:
- Add support untuk Elliptic Curve Cryptography (ECC)
- Implement key rotation mechanism
- Add certificate-based authentication (X.509)
- Support untuk multiple authentication factors (2FA/MFA)

## 📞 Support

Questions? Issues? Open an issue atau kontak developer.

---

**⚡ Built with cryptography library - Production-grade crypto for Python**
