import base64
import pyotp
import time

def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify TOTP code with time window tolerance
    """
    try:
        # 1. Convert hex seed to bytes
        seed_bytes = bytes.fromhex(hex_seed)
        
        # 2. Convert bytes to base32 encoding
        base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
        
        # 3. Create TOTP object
        totp = pyotp.TOTP(base32_seed)
        
        # 4. Verify code with time window tolerance
        # pyotp.verify() handles the window check automatically.
        # valid_window=1 means it checks the current counter +/- 1 period (30s)
        return totp.verify(code, valid_window=valid_window)
        
    except Exception as e:
        print(f"Verification error: {e}")
        return False

if __name__ == "__main__":
    # --- TEST THE VERIFICATION ---
    try:
        # Load your real seed
        with open("decrypted_seed.txt", "r") as f:
            hex_seed = f.read().strip()
            
        print(f"Loaded Seed: {hex_seed[:10]}...") 

        # Generate a code first (so we have something to verify)
        # We re-use the logic from the previous step just for this test
        seed_bytes = bytes.fromhex(hex_seed)
        base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
        totp = pyotp.TOTP(base32_seed)
        current_code = totp.now()
        
        print(f"Generated Code: {current_code}")
        
        # Now verify it
        is_valid = verify_totp_code(hex_seed, current_code)
        
        if is_valid:
            print("✅ Verification Result: TRUE (Code is valid)")
        else:
            print("❌ Verification Result: FALSE (Code is invalid)")

        # Test an invalid code to be sure
        print("Testing invalid code '000000'...")
        print(f"Result: {verify_totp_code(hex_seed, '000000')}")

    except FileNotFoundError:
        print("❌ Error: 'decrypted_seed.txt' not found.")