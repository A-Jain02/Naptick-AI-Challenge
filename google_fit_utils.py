# src/google_fit_utils.py

import os
import pickle
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from googleapiclient.discovery import build
import dateparser

def _load_token():
    with open("token.pickle", "rb") as token_file:
        return pickle.load(token_file)

def fetch_steps_on_date(date_str):
    """Fetch total steps for a specific date string (e.g. 'April 25')"""

    SCOPES = ['https://www.googleapis.com/auth/fitness.activity.read']
    IST = ZoneInfo("Asia/Kolkata")

    # Load credentials
    with open("token.pickle", "rb") as token_file:
        creds = pickle.load(token_file)

    service = build("fitness", "v1", credentials=creds)

    now_ist = datetime.now(IST)
    start_of_day = datetime(now_ist.year, now_ist.month, now_ist.day, tzinfo=IST)
    end_of_day = now_ist

    parsed = dateparser.parse(date_str, settings={"TIMEZONE": "Asia/Kolkata", "RETURN_AS_TIMEZONE_AWARE": True})
    if not parsed:
      return None

    start_of_day = parsed.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    start_ns = int(start_of_day.astimezone(ZoneInfo("UTC")).timestamp() * 1e9)
    end_ns = int(end_of_day.astimezone(ZoneInfo("UTC")).timestamp() * 1e9)
    dataset_id = f"{start_ns}-{end_ns}"

    data_source_id = "derived:com.google.step_count.delta:com.google.android.gms:merge_step_deltas"
    service = build("fitness", "v1", credentials=_load_token())

    dataset = service.users().dataSources().datasets().get(
        userId='me',
        dataSourceId=data_source_id,
        datasetId=dataset_id
    ).execute()

    total_steps = sum(int(p["value"][0]["intVal"]) for p in dataset.get("point", []))
    return total_steps


