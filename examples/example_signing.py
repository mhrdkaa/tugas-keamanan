"""
Example 2: Document Signing & Verification
Digital signature untuk kontrak/dokumen penting.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from crypto_auth import RSAManager


def main():
    print("=" * 60)
    print("  DOCUMENT SIGNING DEMO")
    print("=" * 60)

    # --- Generate signing keypair (CEO/Notary) ---
    ceo_priv, ceo_pub = RSAManager.generate_keypair()
    print("\n[KEY] CEO signing keypair generated (RSA-4096)")

    # --- Export keys (save to files in production) ---
    ceo_priv_pem = RSAManager.private_to_pem(ceo_priv, password="ceo_master_key")
    ceo_pub_pem = RSAManager.public_to_pem(ceo_pub)
    print(f"      Private key: {len(ceo_priv_pem)} bytes (encrypted)")
    print(f"      Public key:  {len(ceo_pub_pem)} bytes")

    # --- Document to sign ---
    contract = """
KONTRAK KERJASAMA
=================

Pihak Pertama: PT. Maju Jaya
Pihak Kedua: PT. Sukses Makmur

Pasal 1:
Kedua belah pihak sepakat untuk bekerjasama dalam proyek XYZ.

Pasal 2:
Nilai kontrak: Rp 1.000.000.000,- (Satu Miliar Rupiah)

Pasal 3:
Jangka waktu: 12 bulan terhitung sejak tanggal ditandatangani.

Ditandatangani pada: 2026-06-19
    """.strip()

    print(f"\n[DOC] Contract document ({len(contract)} chars)")
    print(f"      Preview: {contract[:80]}...")

    # --- Sign document ---
    signature = RSAManager.sign(contract, ceo_priv)
    print(f"\n[SIGN] Document signed by CEO")
    print(f"       Signature: {signature[:60]}...")

    # --- Verify signature ---
    is_valid = RSAManager.verify(contract, signature, ceo_pub)
    print(f"\n[VERIFY] Signature valid: {is_valid}")

    # --- Tamper detection ---
    tampered_contract = contract.replace("Rp 1.000.000.000", "Rp 9.999.999.999")
    tampered_valid = RSAManager.verify(tampered_contract, signature, ceo_pub)
    print(f"[TAMPER] Tampered document valid: {tampered_valid}")

    # --- Save signed document ---
    signed_doc = {
        'document': contract,
        'signature': signature,
        'signer_public_key': ceo_pub_pem.decode('utf-8'),
    }
    print(f"\n[SAVE] Signed document package ready for distribution")
    print(f"       (In production: save as JSON/file)")

    # --- Third-party verification ---
    print("\n[THIRD-PARTY VERIFICATION]")
    third_party_pub = RSAManager.load_public_key(ceo_pub_pem)
    verified = RSAManager.verify(
        signed_doc['document'],
        signed_doc['signature'],
        third_party_pub,
    )
    print(f"  Document verified by third party: {verified}")

    print("\n" + "=" * 60)
    print("  DEMO COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
