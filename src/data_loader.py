import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


def load_json(filename):
    """Load a JSON file from the data directory."""
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_all_collections():
    """Loads all data collections into a dictionary."""
    return {
        "wearable_data": load_json("wearable_data.json"),
        "chat_history": load_json("chat_history.json"),
        "user_profile": load_json("user_profile.json"),
        "location_data": load_json("location_data.json"),
        "wellness_notes": load_json("wellness_notes.json"),
        "mood_and_stress": load_json("mood_and_stress.json")
    }


# For quick test
if __name__ == "__main__":
    data = load_all_collections()
    for key, value in data.items():
        print(f"\n{key.upper()}:")
        print(value[:2] if isinstance(value, list) else value)

