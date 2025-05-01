import json
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 🔐 Step 1: Define SCOPES at the top
SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.heart_rate.read',
    'https://www.googleapis.com/auth/fitness.sleep.read'
]

# 🔐 Step 2: Load credentials and run OAuth flow
flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
creds = flow.run_local_server(port=8080)

# Save token after login
with open("token.pickle", "wb") as token_file:
    pickle.dump(creds, token_file)


# 🔐 Step 3: Connect to Google Fit API
service = build('fitness', 'v1', credentials=creds)

# After: service = build('fitness', 'v1', credentials=creds)

service = build('fitness', 'v1', credentials=creds)

print("✅ Authenticated successfully!")

# List data sources
sources = service.users().dataSources().list(userId='me').execute()
for source in sources.get('dataSource', []):
    print("➤", source['dataStreamId'])



