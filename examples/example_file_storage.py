"""
Example 3: Secure File Storage
Enkripsi file sebelum upload ke cloud storage.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from crypto_auth import AESManager


def main():
    print("=" * 60)
    print("  SECURE FILE STORAGE DEMO")
    print("=" * 60)

    # --- Create sample files ---
    files = {
        'confidential.txt': 'Data rahasia perusahaan:\n\nKaryawan: 500 orang\nRevenue: $10M\nProfit: $2M',
        'passwords.txt': 'Admin Password: super_secret_123\nDB Password: db_pass_456\nAPI Key: key_789',
        'medical.txt': 'Rekam Medis Pasien\nNama: John Doe\nDiagnosa: Confidential\nObat: Confidential',
    }

    print("\n[CREATE] Creating sample sensitive files...")
    for filename, content in files.items():
        with open(filename, 'w') as f:
            f.write(content)
        print(f"         {filename} ({len(content)} bytes)")

    # --- Generate encryption key ---
    key = AESManager.generate_key()
    key_str = AESManager.key_to_base64(key)
    print(f"\n[KEY] Master encryption key generated")
    print(f"      Key (base64): {key_str}")
    print(f"      IMPORTANT: Store this key in secure vault (AWS KMS, Azure Key Vault, etc.)")

    # --- Encrypt all files ---
    print(f"\n[ENCRYPT] Encrypting files for cloud storage...")
    for filename in files.keys():
        enc_file = AESManager.encrypt_file(filename, key)
        original_size = os.path.getsize(filename)
        encrypted_size = os.path.getsize(enc_file)
        print(f"          {filename} -> {enc_file}")
        print(f"          Original: {original_size} bytes | Encrypted: {encrypted_size} bytes")

    # --- Simulate cloud upload ---
    print(f"\n[UPLOAD] Simulating upload to cloud storage...")
    print(f"         (In production: upload *.enc files to S3/Azure/GCS)")

    # --- Delete original files (only keep encrypted) ---
    print(f"\n[CLEANUP] Deleting original unencrypted files...")
    for filename in files.keys():
        os.remove(filename)
        print(f"          Deleted: {filename}")

    # --- Simulate download & decrypt ---
    print(f"\n[DOWNLOAD] Simulating download from cloud...")
    print(f"           (In production: download *.enc files from cloud)")

    print(f"\n[DECRYPT] Decrypting files for use...")
    for filename in files.keys():
        enc_file = filename + '.enc'
        dec_file = AESManager.decrypt_file(enc_file, key)
        print(f"          {enc_file} -> {dec_file}")

    # --- Verify content ---
    print(f"\n[VERIFY] Verifying decrypted content...")
    for filename, original_content in files.items():
        dec_file = filename + '.enc.dec'
        with open(dec_file, 'r') as f:
            decrypted_content = f.read()
        match = decrypted_content == original_content
        print(f"         {filename}: {'OK' if match else 'FAILED'}")

    # --- Cleanup ---
    print(f"\n[CLEANUP] Removing test files...")
    for filename in files.keys():
        for ext in ['.enc', '.enc.dec']:
            test_file = filename + ext
            if os.path.exists(test_file):
                os.remove(test_file)

    print(f"\n[SUMMARY]")
    print(f"  1. Files encrypted with AES-256-GCM")
    print(f"  2. Only encrypted versions uploaded to cloud")
    print(f"  3. Master key stored in secure vault (HSM/KMS)")
    print(f"  4. Even if cloud is breached, data remains secure")
    print(f"  5. Authenticated encryption prevents tampering")

    print("\n" + "=" * 60)
    print("  DEMO COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
