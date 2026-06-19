from crypto_auth import RSAManager

# Generate keypair sendiri
my_private_key, my_public_key = RSAManager.generate_keypair()

# Save private key (JANGAN COMMIT KE GIT!)
private_pem = RSAManager.private_to_pem(my_private_key, password="your-password")
with open("my_private_key.pem", "wb") as f:
    f.write(private_pem)
