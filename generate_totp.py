import base64
import pyotp
import time

def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current TOTP code from hex seed
    """
    # 1. Convert hex seed to bytes
    # The instructions require parsing the 64-char hex string to bytes first
    try:
        seed_bytes = bytes.fromhex(hex_seed)
    except ValueError:
        return "Error: Invalid hex seed"

    # 2. Convert bytes to base32 encoding
    # pyotp requires a base32 encoded string (not bytes) to initialize
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8')

    # 3. Create TOTP object
    # Default settings for pyotp match the requirements:
    # - Algorithm: SHA-1 (default)
    # - Period: 30 seconds (default)
    # - Digits: 6 (default)
    totp = pyotp.TOTP(base32_seed)

    # 4. Generate current TOTP code
    return totp.now()

if __name__ == "__main__":
    # Automatically read the decrypted seed you generated in the last step
    try:
        with open("decrypted_seed.txt", "r") as f:
            hex_seed = f.read().strip()
            
        print(f"Using Seed: {hex_seed}")
        print("-" * 30)
        
        # Generate the code
        code = generate_totp_code(hex_seed)
        
        print(f"🔐 Current TOTP Code: {code}")
        print(f"   (Valid for 30 seconds)")
        print("-" * 30)
        
    except FileNotFoundError:
        print("❌ Error: 'decrypted_seed.txt' not found. Make sure you ran decrypt_seed.py first.")