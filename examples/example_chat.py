"""
Example 1: Secure Messaging App
Simulasi chat app dengan enkripsi end-to-end seperti WhatsApp/Signal.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from crypto_auth import (
    AuthServer, AuthClient, RSAManager, HybridEncryptor, SecureChannel
)


def main():
    print("=" * 60)
    print("  SECURE MESSAGING APP DEMO")
    print("=" * 60)

    # --- Setup Server ---
    server = AuthServer("chat-server-01")
    server.register_user("alice", "alice_secret_123")
    server.register_user("bob", "bob_secret_456")
    print("\n[SETUP] Chat server ready. Users: alice, bob")

    # --- Login ---
    alice = AuthClient("alice", server.get_public_key_pem())
    bob = AuthClient("bob", server.get_public_key_pem())

    alice.login(server, "alice_secret_123")
    bob.login(server, "bob_secret_456")
    print("[AUTH]  Alice & Bob logged in successfully")

    # --- Establish Secure Channel (like WhatsApp E2E) ---
    alice_channel = SecureChannel(alice.private_key, bob.public_key)
    bob_channel = SecureChannel(bob.private_key, alice.public_key)

    handshake = alice_channel.initiate()
    bob_channel.accept(handshake)
    print("[E2E]   End-to-end encrypted channel established!\n")

    # --- Chat Session ---
    messages = [
        ("alice", "Hai Bob! Apa kabar?"),
        ("bob", "Hai Alice! Baik, kamu gimana?"),
        ("alice", "Baik juga! Mau meeting jam 3 ya."),
        ("bob", "Siap, sampai ketemu di meeting room."),
    ]

    print("-" * 60)
    print("  CHAT SESSION")
    print("-" * 60)

    for sender, text in messages:
        if sender == "alice":
            encrypted = alice_channel.send(text)
            received = bob_channel.receive(encrypted)
            print(f"  Alice -> Bob:   {received}")
        else:
            encrypted = bob_channel.send(text)
            received = alice_channel.receive(encrypted)
            print(f"  Bob   -> Alice: {received}")

    print("-" * 60)

    # --- Send signed + encrypted message ---
    print("\n[SIGNED MESSAGE]")
    packet = alice.send_encrypted_message(
        "Dokumen proyek sudah saya kirim. - Alice", server
    )
    received = AuthClient.receive_encrypted_message(packet, server)
    print(f"  Server received: {received}")

    # --- Verify signature ---
    print(f"\n  [INFO] Message integrity verified via RSA signature")
    print(f"  [INFO] Data encrypted with AES-256-GCM (fast)")
    print(f"  [INFO] AES key protected with RSA-4096 (secure)")

    print("\n" + "=" * 60)
    print("  DEMO COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
