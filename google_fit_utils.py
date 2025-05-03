import os
import pickle
import dateparser
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from googleapiclient.discovery import build

def _load_token():
    with open("token.pickle", "rb") as token_file:
        return pickle.load(token_file)

def fetch_steps_on_date(date_str):
    # Parse the natural language date to a timezone-aware datetime object
    parsed = dateparser.parse(
        date_str,
        settings={
            "TIMEZONE": "Asia/Kolkata",
            "RETURN_AS_TIMEZONE_AWARE": True
        }
    )
    if not parsed:
        return None

    # Compute exact window for the day (in IST)
    start_of_day = parsed.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    # Convert window to UTC nanoseconds
    start_ns = int(start_of_day.astimezone(ZoneInfo("UTC")).timestamp() * 1e9)
    end_ns = int(end_of_day.astimezone(ZoneInfo("UTC")).timestamp() * 1e9)
    dataset_id = f"{start_ns}-{end_ns}"

    # Build service fresh per call
    creds = _load_token()
    service = build("fitness", "v1", credentials=creds)

    data_source_id = "derived:com.google.step_count.delta:com.google.android.gms:merge_step_deltas"
    print(f"🧪 Fetching steps for: {date_str}")
    print(f"⏳ Start (IST): {start_of_day}")
    print(f"⏳ End   (IST): {end_of_day}")
    print(f"🕓 Now: {datetime.now(ZoneInfo('Asia/Kolkata'))}")

    dataset = service.users().dataSources().datasets().get(
        userId='me',
        dataSourceId=data_source_id,
        datasetId=dataset_id
    ).execute()

    print(f"📦 Data points fetched: {len(dataset.get('point', []))}")

    total_steps = sum(int(p["value"][0]["intVal"]) for p in dataset.get("point", []))
    return total_steps