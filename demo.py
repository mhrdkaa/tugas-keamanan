"""
CryptoAuth Demo - Demonstrates all features of the hybrid auth system.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crypto_auth.symmetric import AESManager
from crypto_auth.asymmetric import RSAManager, HybridEncryptor
from crypto_auth.auth_protocol import AuthServer, AuthClient, SecureChannel


def separator(title):
    width = 70
    print(f"\n{'=' * width}")
    print(f"  {title}")
    print(f"{'=' * width}\n")


def demo_symmetric_aes():
    separator("DEMO 1: AES-256-GCM SYMMETRIC ENCRYPTION")
    key = AESManager.generate_key()
    print(f"[KEY] AES Key (base64): {AESManager.key_to_base64(key)}")
    print(f"      Key length: {len(key)} bytes ({len(key) * 8} bits)")

    secret_msg = "Ini adalah pesan rahasia yang dienkripsi dengan AES-256-GCM!"
    print(f"\n[IN] Plaintext: {secret_msg}")

    encrypted = AESManager.encrypt(secret_msg, key)
    print(f"[ENC] Ciphertext (base64): {encrypted['ciphertext'][:50]}...")
    print(f"      Nonce (base64):       {encrypted['nonce']}")
    print(f"      Tag (base64):         {encrypted['tag']}")

    decrypted = AESManager.decrypt(encrypted, key)
    print(f"\n[DEC] Decrypted: {decrypted}")
    print(f"[OK]  Match: {secret_msg == decrypted}")

    print(f"\n[TEST] Tamper Detection:")
    tampered = dict(encrypted)
    tampered['ciphertext'] = tampered['ciphertext'][:-3] + 'XXX'
    try:
        AESManager.decrypt(tampered, key)
        print("   FAIL: No error on tampered data!")
    except Exception as e:
        print(f"   PASS: Detected tampering -> {type(e).__name__}")


def demo_asymmetric_rsa():
    separator("DEMO 2: RSA-4096 ASYMMETRIC ENCRYPTION & SIGNING")
    priv_key, pub_key = RSAManager.generate_keypair()
    print(f"[RSA] Keypair generated ({RSAManager.KEY_SIZE}-bit)")

    priv_pem = RSAManager.private_to_pem(priv_key)
    pub_pem = RSAManager.public_to_pem(pub_key)
    print(f"      Private key PEM: {len(priv_pem)} bytes")
    print(f"      Public key PEM:  {len(pub_pem)} bytes")

    message = "Pesan ini ditandatangani dengan RSA!"
    signature = RSAManager.sign(message, priv_key)
    print(f"\n[IN] Message: {message}")
    print(f"[SIG] Signature (base64): {signature[:60]}...")

    valid = RSAManager.verify(message, signature, pub_key)
    print(f"[OK]  Signature valid: {valid}")

    fake_valid = RSAManager.verify(message + "tampered", signature, pub_key)
    print(f"[OK]  Tampered message valid: {fake_valid}")


def demo_hybrid_encryption():
    separator("DEMO 3: HYBRID ENCRYPTION (RSA + AES)")
    priv_key, pub_key = RSAManager.generate_keypair()
    secret = "Data besar dan rahasia ini dienkripsi hybrid - RSA untuk kunci AES, AES untuk data."

    print(f"[IN] Original: {secret}")
    encrypted = HybridEncryptor.encrypt(secret, pub_key)

    print(f"[ENC] Encrypted AES key:  {encrypted['encrypted_aes_key'][:50]}...")
    print(f"      Ciphertext:         {encrypted['ciphertext'][:50]}...")

    decrypted = HybridEncryptor.decrypt(encrypted, priv_key)
    print(f"\n[DEC] Decrypted: {decrypted}")
    print(f"[OK]  Match: {secret == decrypted}")


def demo_auth_protocol():
    separator("DEMO 4: AUTHENTICATION PROTOCOL (Full Flow)")
    server = AuthServer("my-secure-server")
    print(f"[SERVER] Server [{server.get_server_id()}] started")

    server.register_user("alice", "s3cur3_p@ss!")
    print(f"[USER] 'alice' registered")

    client = AuthClient("alice", server.get_public_key_pem())
    login_ok = client.login(server, "s3cur3_p@ss!")
    print(f"[LOGIN] Successful: {login_ok}")

    print(f"\n[SEND] Alice sends encrypted message to server...")
    packet = client.send_encrypted_message(
        "Halo Server! Ini pesan rahasia dari Alice.", server
    )
    print(f"       Packet size: {len(str(packet))} bytes")

    received = AuthClient.receive_encrypted_message(packet, server)
    print(f"[RECV] Server received: {received}")

    print(f"\n[TEST] Expired token rejection...")
    client.current_token.expires_at = 0
    try:
        client.send_encrypted_message("test", server)
        print("       FAIL!")
    except PermissionError as e:
        print(f"       PASS: {e}")

    print(f"\n[TEST] Wrong password...")
    client2 = AuthClient("alice", server.get_public_key_pem())
    login_ok = client2.login(server, "wrong_password")
    print(f"       Login successful: {login_ok}")


def demo_secure_channel():
    separator("DEMO 5: SECURE CHANNEL (Session Key Exchange)")
    alice_priv, alice_pub = RSAManager.generate_keypair()
    bob_priv, bob_pub = RSAManager.generate_keypair()
    print("[SETUP] Alice & Bob each generated RSA keypairs")

    alice_channel = SecureChannel(alice_priv, bob_pub)
    bob_channel = SecureChannel(bob_priv, alice_pub)

    print("\n[HSHAKE] Alice sends encrypted session key to Bob...")
    handshake = alice_channel.initiate()
    bob_channel.accept(handshake)
    print("         Secure channel established (AES key exchanged via RSA)")

    alice_msg = "Hai Bob! Ini channel aman kita."
    print(f"\n[ALICE] {alice_msg}")
    encrypted = alice_channel.send(alice_msg)
    print(f"        Encrypted (base64): {encrypted['ciphertext'][:40]}...")

    bob_received = bob_channel.receive(encrypted)
    print(f"[BOB]   Bob received: {bob_received}")

    bob_reply = "Halo Alice! Pesanmu aman sampai."
    print(f"\n[BOB]   {bob_reply}")
    encrypted_reply = bob_channel.send(bob_reply)
    alice_received = alice_channel.receive(encrypted_reply)
    print(f"[ALICE] Alice received: {alice_received}")


def demo_file_encryption():
    separator("DEMO 6: FILE ENCRYPTION")
    test_file = "test_secret.txt"
    enc_file = "test_secret.txt.enc"
    dec_file = "test_secret.txt.dec"

    with open(test_file, 'w') as f:
        f.write("Ini adalah file rahasia yang dienkripsi dengan AES-256-GCM.\n")
        f.write("Hanya pemilik kunci yang bisa membacanya.\n")

    key = AESManager.generate_key()
    print(f"[KEY] AES Key: {AESManager.key_to_base64(key)}")

    result = AESManager.encrypt_file(test_file, key)
    print(f"[ENC] Encrypted: {result} ({os.path.getsize(result)} bytes)")

    result = AESManager.decrypt_file(enc_file, key)
    print(f"[DEC] Decrypted: {result}")

    with open(dec_file, 'r') as f:
        content = f.read()
    print(f"      Content: {content.strip()}")

    for f in [test_file, enc_file, dec_file]:
        if os.path.exists(f):
            os.remove(f)


def main():
    print(f"\n{'#' * 70}")
    print(f"#     CryptoAuth - Hybrid Authentication System Demo        #")
    print(f"#     Symmetric (AES-256-GCM) + Asymmetric (RSA-4096)       #")
    print(f"{'#' * 70}")

    demo_symmetric_aes()
    demo_asymmetric_rsa()
    demo_hybrid_encryption()
    demo_auth_protocol()
    demo_secure_channel()
    demo_file_encryption()

    separator("ALL DEMOS COMPLETED SUCCESSFULLY")
    print("""
  Summary:
  - AES-256-GCM: Fast symmetric encryption with auth tag (integrity)
  - RSA-4096:    Asymmetric encryption + digital signatures
  - Hybrid:      RSA encrypts AES key, AES encrypts bulk data
  - Auth Token:  RSA-signed JWT-like tokens with expiry
  - Secure Chan: RSA key exchange -> fast AES session
  - File Enc:    AES-256-GCM file encryption/decryption
    """)


if __name__ == '__main__':
    main()
