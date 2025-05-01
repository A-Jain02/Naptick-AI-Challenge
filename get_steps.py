import os
import pickle
import time
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Google Fit scopes
SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.heart_rate.read',
    'https://www.googleapis.com/auth/fitness.sleep.read'
]

# Authenticate using saved token or run new OAuth flow
if os.path.exists("token.pickle"):
    with open("token.pickle", "rb") as token_file:
        creds = pickle.load(token_file)
else:
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
    creds = flow.run_local_server(port=8080)
    with open("token.pickle", "wb") as token_file:
        pickle.dump(creds, token_file)

service = build('fitness', 'v1', credentials=creds)

# Time zone info
IST = ZoneInfo("Asia/Kolkata")

# Repeated polling every 60 seconds
def fetch_step_total():
    now_ist = datetime.now(IST)
    start_of_day_ist = datetime(now_ist.year, now_ist.month, now_ist.day, tzinfo=IST)
    end_of_day_ist = now_ist

    # Convert to UTC
    start_ns = int(start_of_day_ist.astimezone(ZoneInfo("UTC")).timestamp() * 1e9)
    end_ns = int(end_of_day_ist.astimezone(ZoneInfo("UTC")).timestamp() * 1e9)
    dataset_id = f"{start_ns}-{end_ns}"

    # Fetch step data
    data_source_id = "derived:com.google.step_count.delta:com.google.android.gms:merge_step_deltas"
    dataset = service.users().dataSources().datasets().get(
        userId='me',
        dataSourceId=data_source_id,
        datasetId=dataset_id
    ).execute()
    print(f"🔄 Fetched at {datetime.now(IST).strftime('%H:%M:%S')} (cloud may be delayed)")


    total_steps = sum(
        int(point["value"][0]["intVal"])
        for point in dataset.get("point", [])
    )

    # Define path to data file
    DATA_PATH = os.path.join("data", "wearable_data.json")

    # Build new entry
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "steps": f"{total_steps} steps"
    }

    # Load existing data
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Append new entry and save
    data.append(entry)

    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print("✅ Step count added to wearable_data.json")

    return total_steps


print("\n📡 Starting real-time step tracker (refreshes every 60 seconds)");
try:
    while True:
        current_steps = fetch_step_total()
        now_time = datetime.now(IST).strftime("%H:%M:%S")
        print(f"[{now_time}] 🪜 Steps so far today: {current_steps}")
        time.sleep(60)
except KeyboardInterrupt:
    print("\n🛑 Real-time tracking stopped.")