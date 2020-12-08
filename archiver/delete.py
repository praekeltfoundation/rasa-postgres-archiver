import logging
from datetime import date, datetime, timedelta, timezone

from archiver import settings
from archiver.archive import get_existing_archives, get_oldest_event_timestamp

logger = logging.getLogger(__name__)


def delete_day(conn, day):
    """
    Deletes all events for the UTC day
    """
    day_start = datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc)
    next_day = day_start + timedelta(days=1)

    logger.info(f"Deleting events for {day.isoformat()}...")

    with conn.cursor() as cur:
        cur.execute(
            """
            WITH deleted AS (
                DELETE FROM events
                WHERE timestamp >= %s AND timestamp < %s
                RETURNING *
            ) SELECT count(*) from deleted
            """,
            (day_start.timestamp(), next_day.timestamp()),
        )
        [count] = cur.fetchone()

    logger.info(f"Deleted {count} events for {day.isoformat()}")


def delete_events(psql_conn, s3bucket):
    """
    Finds which events we already have archives for, and deletes them
    """
    archive_date = get_oldest_event_timestamp(psql_conn).date()
    database_dates = set()
    while archive_date <= date.today() - timedelta(days=settings.RETENTION_DAYS):
        database_dates.add(archive_date)
        archive_date += timedelta(days=1)

    existing_archives = set(get_existing_archives(s3bucket))

    dates_to_delete = database_dates & existing_archives
    for day in sorted(dates_to_delete):
        delete_day(psql_conn, day)
