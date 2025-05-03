import time
from datetime import datetime
from zoneinfo import ZoneInfo
from google_fit_utils import fetch_steps_on_date  # This must be defined separately
import dateparser

POLL_INTERVAL = 60  # seconds
IST = ZoneInfo("Asia/Kolkata")

def main():
    seen_steps = None
    while True:
        now = datetime.now(IST)
        date_str = now.strftime("%Y-%m-%d")
        steps = fetch_steps_on_date(date_str)

        if steps is not None and steps != seen_steps:
            print(f"🕓 {now.strftime('%Y-%m-%d %H:%M:%S IST')} | Steps: {steps}")
            seen_steps = steps

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()