import base64
import string
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP
    """
    try:
        # 1. Base64 decode the encrypted seed string
        ciphertext = base64.b64decode(encrypted_seed_b64)

        # 2. RSA/OAEP decrypt with SHA-256
        # Critical Parameters from instructions:
        # - Padding: OAEP
        # - MGF: MGF1 with SHA-256
        # - Hash: SHA-256
        # - Label: None
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # 3. Decode bytes to UTF-8 string
        decrypted_seed = plaintext.decode('utf-8')

        # 4. Validate: must be 64-character hex string
        if len(decrypted_seed) != 64:
            raise ValueError(f"Invalid seed length: {len(decrypted_seed)} (expected 64)")
        
        # Check if all characters are valid hex digits (0-9, a-f, A-F)
        if not all(c in string.hexdigits for c in decrypted_seed):
             raise ValueError("Seed contains non-hex characters")

        return decrypted_seed

    except Exception as e:
        print(f"❌ Decryption failed: {e}")
        return None

if __name__ == "__main__":
    # --- LOAD PRIVATE KEY ---
    print("Loading private key...")
    try:
        with open("student_private.pem", "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None
            )
    except FileNotFoundError:
        print("❌ Error: 'student_private.pem' not found.")
        exit(1)

    # --- READ ENCRYPTED SEED ---
    print("Reading encrypted seed...")
    try:
        with open("encrypted_seed.txt", "r") as f:
            encrypted_seed_b64 = f.read().strip()
    except FileNotFoundError:
        print("❌ Error: 'encrypted_seed.txt' not found.")
        exit(1)

    # --- DECRYPT ---
    print("Decrypting...")
    plain_seed = decrypt_seed(encrypted_seed_b64, private_key)

    if plain_seed:
        print("\n✅ SUCCESS! Decrypted Seed:")
        print("----------------------------------------------------------------")
        print(plain_seed)
        print("----------------------------------------------------------------")
        
        # Optional: Save it purely for your own convenience (do not commit this!)
        with open("decrypted_seed.txt", "w") as f:
            f.write(plain_seed)
        print("\n(Saved to 'decrypted_seed.txt' - DO NOT COMMIT THIS FILE)")