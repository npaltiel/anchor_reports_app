from firebase_setup import database
from datetime import datetime, timezone


def log_run(results):
    """Log the run details to Firebase Realtime Database."""
    ref = database.reference("/caregiver_team_logs")
    ref.push({
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "results": results
    })
