import base64
import pyotp
import datetime
import pytz
import os

# Path required by Step 10 instructions
SEED_FILE_PATH = "/data/seed.txt"

def get_totp_code(hex_seed):
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
    totp = pyotp.TOTP(base32_seed)
    return totp.now()

def main():
    # 1. Read hex seed from persistent storage
    try:
        if not os.path.exists(SEED_FILE_PATH):
            print(f"CRON: {SEED_FILE_PATH} not found. Skipping.")
            return
            
        with open(SEED_FILE_PATH, "r") as f:
            hex_seed = f.read().strip()
            
        # 2. Generate current TOTP code
        code = get_totp_code(hex_seed)
        
        # 3. Get current UTC timestamp (Critical requirement)
        utc_now = datetime.datetime.now(pytz.utc)
        timestamp = utc_now.strftime("%Y-%m-%d %H:%M:%S")
        
        # 4. Output formatted line (Matches screenshot requirement)
        # Format: "(timestamp) - 2FA Code: {code}"
        print(f"({timestamp}) - 2FA Code: {code}")

    except Exception as e:
        print(f"CRON Error: {e}")

if __name__ == "__main__":
    main()