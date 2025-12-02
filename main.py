from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_rsa_keypair(key_size: int = 4096):
    """
    Generate RSA key pair with 4096 bits and 65537 exponent.
    """
    # 1. Generate the private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )

    # 2. Derive the public key
    public_key = private_key.public_key()

    return private_key, public_key

if __name__ == "__main__":
    print("Generating RSA key pair... this might take a moment.")
    
    # Call the function
    priv_key_obj, pub_key_obj = generate_rsa_keypair()

    # --- SAVE PRIVATE KEY ---
    # Serialize to PEM format (PKCS8 is standard for private keys)
    pem_private = priv_key_obj.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    with open("student_private.pem", "wb") as f:
        f.write(pem_private)
    
    # --- SAVE PUBLIC KEY ---
    # Serialize to PEM format (SubjectPublicKeyInfo is standard for public keys)
    pem_public = pub_key_obj.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    with open("student_public.pem", "wb") as f:
        f.write(pem_public)

    print("Success! Created 'student_private.pem' and 'student_public.pem'")