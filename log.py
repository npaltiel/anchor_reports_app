import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import json
import os

# Firebase setup - Load credentials from environment variables (for deployment)
if "FIREBASE_CREDENTIALS" in os.environ:
    firebase_config = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
    cred = credentials.Certificate(firebase_config)
else:
    # Local development: Use the credentials file
    cred = credentials.Certificate("firebase_credentials.json")

# Initialize Firebase
firebase_admin.initialize_app(cred, {
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL")
})

def log_run(results):
    """Log the run details to Firebase Realtime Database."""
    ref = db.reference("/logs")
    ref.push({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "results": results
    })
