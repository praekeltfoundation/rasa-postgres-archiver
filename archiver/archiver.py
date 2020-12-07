import gzip
import logging
import os
import re
import tempfile
from datetime import date, datetime, timedelta, timezone

from . import settings


def create_day_archive(conn, file, day):
    """
    Creates an archive for the specified day, using UTC
    conn: postgresql connection
    file: file object to write output to
    day: datetime.date of the day the archive is for
    """
    day_start = datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc)
    next_day = day_start + timedelta(days=1)
    count = 0

    logging.info(f"Creating event archive for {day.isoformat()}...")

    with conn.cursor(f"archive-{day.isoformat()}") as cur:
        cur.execute(
            """
            SELECT row_to_json(event)::text FROM (
                SELECT *
                FROM events
                WHERE timestamp >= %s AND timestamp < %s
            ) AS event""",
            (day_start.timestamp(), next_day.timestamp()),
        )
        for row in cur:
            file.write(row[0].encode("utf-8"))
            file.write("\n".encode("utf-8"))
            count += 1
            if count % 10000 == 0:
                logging.info(f"Archived {count} events for {day.isoformat()}")

    logging.info(f"Created event archive for {day.isoformat()}, {count} total events.")


def create_and_upload_day_archive(psql_conn, s3bucket, day):
    """
    Creates a day archive, and uploads it to S3
    psql_conn: postgresql connection
    s3client: the S3 client
    day: datetime.day of the day the archive is for
    """
    _, filename = tempfile.mkstemp(".json.gz")
    try:
        with gzip.open(filename, "w") as file:
            create_day_archive(psql_conn, file, day)
        logging.info(f"Uploading archive for {day.isoformat()}...")
        s3bucket.upload_file(
            filename,
            f"{settings.S3_KEY_PREFIX}-{day.isoformat()}.json.gz",
        )
        logging.info(f"Upload complete for {day.isoformat()}.")
    finally:
        os.remove(filename)


def get_existing_archives(s3bucket):
    """
    Returns a generator that yields all the dates of the existing archives
    """
    for obj in s3bucket.objects.filter(Prefix=settings.S3_KEY_PREFIX):
        match = re.match(f"{settings.S3_KEY_PREFIX}-(?P<date>.+)\\.json\\.gz", obj.key)
        yield date.fromisoformat(match.group("date"))


def get_oldest_event_timestamp(psql_conn):
    """
    Returns the timestamp of the oldest event in the database
    """
    with psql_conn.cursor() as cur:
        cur.execute("SELECT MIN(timestamp) FROM events")
        [timestamp] = cur.fetchone()
        if timestamp:
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def get_archive_dates(psql_conn, s3bucket):
    """
    Returns a set of all the dates that require an archive
    """
    oldest = get_oldest_event_timestamp(psql_conn)
    if not oldest:
        return set()

    archive_date = oldest.date()
    database_dates = set()
    while archive_date <= date.today() - timedelta(days=settings.RETENTION_DAYS):
        database_dates.add(archive_date)
        archive_date += timedelta(days=1)

    return database_dates - set(get_existing_archives(s3bucket))
