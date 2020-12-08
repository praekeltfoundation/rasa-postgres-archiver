import logging
from datetime import date, datetime, timedelta, timezone
from time import sleep

import boto3
import psycopg2

from archiver import archive, settings

logging.basicConfig(level=settings.LOGLEVEL)
logger = logging.getLogger(__name__)


def sleep_until_midnight():
    now = datetime.now(timezone.utc)
    target = datetime.combine(
        date.today() + timedelta(days=1), datetime.min.time(), timezone.utc
    )
    seconds = (target - now).seconds
    logger.info(f"Sleeping for {seconds}s until {target.isoformat()}")
    sleep(seconds)


def loop():
    psql_conn = psycopg2.connect(settings.DATABASE)
    s3bucket = boto3.resource("s3", region_name=settings.S3_REGION).Bucket(
        settings.S3_BUCKET
    )
    while True:
        sleep_until_midnight()
        archive.create_archives(psql_conn, s3bucket)


if __name__ == "__main__":
    loop()
