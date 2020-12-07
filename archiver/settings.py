import os

DATABASE = os.getenv("DATABASE", "postgres://")
S3_BUCKET = os.getenv("S3_BUCKET", "rasa-archive")
S3_KEY_PREFIX = os.getenv("S3_KEY_PREFIX", "events")
