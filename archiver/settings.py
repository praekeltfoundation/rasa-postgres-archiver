import os

DATABASE = os.getenv("DATABASE", "postgres://")
S3_BUCKET = os.getenv("S3_BUCKET", "rasa-archive")
S3_KEY_PREFIX = os.getenv("S3_KEY_PREFIX", "events")
S3_REGION = os.getenv("S3_REGION")
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "30"))
LOGLEVEL = os.getenv("LOGLEVEL", "INFO")
DELETE = os.getenv("DELETE", "false").lower() == "true"
