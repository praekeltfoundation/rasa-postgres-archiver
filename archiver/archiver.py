import gzip
import logging
import os
import tempfile
from datetime import datetime, timedelta, timezone

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


def create_and_upload_day_archive(psql_conn, s3client, day):
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
        s3client.upload_file(
            filename, settings.S3_BUCKET, f"events-{day.isoformat()}.json.gz"
        )
        logging.info(f"Upload complete for {day.isoformat()}.")
    finally:
        os.remove(filename)
