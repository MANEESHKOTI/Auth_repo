import requests
import json

def request_seed(student_id: str, github_repo_url: str, api_url: str):
    """
    Request encrypted seed from instructor API
    """
    # Step 1: Read student public key from PEM file
    try:
        with open("student_public.pem", "r") as f:
            public_key_content = f.read()
    except FileNotFoundError:
        print("❌ Error: 'student_public.pem' not found.")
        return

    # Step 2: Prepare HTTP POST request payload
    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key_content
    }

    # Step 3: Send POST request to instructor API
    print(f"Connecting to Instructor API...")
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        
        # Step 4: Parse JSON response
        if response.status_code == 200:
            data = response.json()
            if "encrypted_seed" in data:
                encrypted_seed = data["encrypted_seed"]
                print("✅ Success! Encrypted seed received.")
                
                # Step 5: Save encrypted seed to file
                with open("encrypted_seed.txt", "w") as f:
                    f.write(encrypted_seed)
                print("💾 Saved to 'encrypted_seed.txt'")
            else:
                print("⚠️ Error: Response did not contain 'encrypted_seed'.")
                print("Response:", data)
        else:
            print(f"❌ Failed with status code {response.status_code}")
            print("Response:", response.text)

    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    # --- FILL IN YOUR DETAILS HERE ---
    STUDENT_ID = "23A91A4409"  # Replace with your actual ID
    REPO_URL = "https://github.com/MANEESHKOTI/Auth_repo.git"
    API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws/"

    request_seed(STUDENT_ID, REPO_URL, API_URL)