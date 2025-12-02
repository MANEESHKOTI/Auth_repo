import base64
import os
import json
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import pyotp
from fastapi.responses import JSONResponse

app = FastAPI()

# --- CONFIGURATION ---
# We use relative path "./data" for local testing.
# In Docker (Step 8), this will map to the actual /data volume.
SEED_FILE_PATH = "/data/seed.txt"
PRIVATE_KEY_PATH = "student_private.pem"

class SeedRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

@app.post("/decrypt-seed")
def decrypt_seed_endpoint(request: SeedRequest):
    """
    Endpoint 1: POST /decrypt-seed
    Receives encrypted seed, decrypts it, and saves to ./data/seed.txt
    """
    try:
        # 1. Load the private key
        if not os.path.exists(PRIVATE_KEY_PATH):
            raise HTTPException(status_code=500, detail="Private key not found")
            
        with open(PRIVATE_KEY_PATH, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None
            )

        # 2. Base64 decode
        try:
            ciphertext = base64.b64decode(request.encrypted_seed)
        except Exception:
            raise HTTPException(status_code=500, detail="Invalid Base64 input")

        # 3. Decrypt (RSA/OAEP-SHA256)
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        decrypted_seed = plaintext.decode('utf-8')

        # 4. Validate (64-char hex)
        if len(decrypted_seed) != 64:
             raise HTTPException(status_code=500, detail="Decrypted seed length invalid")

        # 5. Save to file
        os.makedirs(os.path.dirname(SEED_FILE_PATH), exist_ok=True)
        with open(SEED_FILE_PATH, "w") as f:
            f.write(decrypted_seed)

        return {"status": "ok"}

    except Exception as e:
        # Match the error format in Screenshot 8.29.08 PM
        return {"error": "Decryption failed", "details": str(e)}

@app.get("/generate-2fa")
def generate_2fa_endpoint():
    """
    Endpoint 2: GET /generate-2fa
    Returns current TOTP code.
    """
    if not os.path.exists(SEED_FILE_PATH):
         # Match error in Screenshot 8.36.31 PM
         raise HTTPException(status_code=500, detail="Seed file not found. Call /decrypt-seed first.")

    try:
        with open(SEED_FILE_PATH, "r") as f:
            hex_seed = f.read().strip()

        seed_bytes = bytes.fromhex(hex_seed)
        base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
        totp = pyotp.TOTP(base32_seed)
        
        return {
            "code": totp.now(),
            "valid_for": 30
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify-2fa")
def verify_2fa_endpoint(request: VerifyRequest):
    """
    Endpoint 3: POST /verify-2fa
    Verifies if the provided code is valid.
    """
    if not request.code:
        # Match error in Screenshot 8.40.45 PM
        return JSONResponse(status_code=400, content={"error": "Missing code"})

    if not os.path.exists(SEED_FILE_PATH):
         # Match error in Screenshot 8.40.45 PM
         return {"error": "Seed not decrypted yet"}

    try:
        with open(SEED_FILE_PATH, "r") as f:
            hex_seed = f.read().strip()

        seed_bytes = bytes.fromhex(hex_seed)
        base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
        
        # Verify with ±1 period tolerance (30s) as per checklist
        totp = pyotp.TOTP(base32_seed)
        is_valid = totp.verify(request.code, valid_window=1)
        
        return {"valid": is_valid}

    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))