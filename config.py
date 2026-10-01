import os

SUBJECTS = [
    "Mathematics",
    "Further Mathematics",
    "Chemistry",
    "Physics",
    "Computer Science",
    "ICT",
]

SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key")

SUPER_ADMIN_USERNAME = os.environ.get("SUPER_ADMIN_USERNAME", "mafa_admin")
SUPER_ADMIN_PASSWORD = os.environ.get("SUPER_ADMIN_PASSWORD", "change-this-password")

# Debug mode must be explicitly enabled via an environment variable.
# Never leave this on in a real deployment -- it exposes an
# interactive code-execution debugger if the app ever crashes.
DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"

PORT = int(os.environ.get("PORT", 5000))
