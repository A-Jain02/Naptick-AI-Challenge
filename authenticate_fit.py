import os
import pickle
import json
import pathlib
from google_auth_oauthlib.flow import InstalledAppFlow

# Path to your credentials.json
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.pickle"

# Scopes required for Google Fit
SCOPES = [
    "https://www.googleapis.com/auth/fitness.activity.read",
    "https://www.googleapis.com/auth/fitness.location.read",
    "https://www.googleapis.com/auth/fitness.body.read"
]

def authenticate():
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ Missing {CREDENTIALS_FILE}. Please place it in this directory.")
        return

    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')

    with open(TOKEN_FILE, "wb") as token:
        pickle.dump(creds, token)

    print("✅ Authentication complete. token.pickle has been saved.")

if __name__ == "__main__":
    authenticate()