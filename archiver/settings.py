import os

DATABASE = os.getenv("DATABASE", "postgres://")
S3_BUCKET = os.getenv("S3_BUCKET", "rasa-archive")
