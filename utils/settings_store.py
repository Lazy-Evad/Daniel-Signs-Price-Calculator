import json
import os

# Path to local settings file (sits alongside main.py)
_SETTINGS_FILE = os.path.join(os.path.dirname(__file__), '..', 'settings.json')
_SETTINGS_FILE = os.path.normpath(_SETTINGS_FILE)

SETTINGS_DEFAULTS = {
    "hourly_rate":   66.04,
    "workshop_rate": 60.00,
    "fitting_rate":  75.00,
    "travel_rate":   75.00,
}

def load_settings_local():
    """Load from local JSON file. Falls back to defaults."""
    try:
        if os.path.exists(_SETTINGS_FILE):
            with open(_SETTINGS_FILE, 'r') as f:
                data = json.load(f)
            return {k: float(data.get(k, v)) for k, v in SETTINGS_DEFAULTS.items()}
    except Exception:
        pass
    return dict(SETTINGS_DEFAULTS)

def save_settings_local(rate_dict):
    """Save to local JSON file."""
    try:
        with open(_SETTINGS_FILE, 'w') as f:
            json.dump({k: float(v) for k, v in rate_dict.items()}, f, indent=2)
        return True
    except Exception as e:
        return False
