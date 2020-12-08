import logging
from datetime import datetime, timedelta, timezone

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
            ) SELECT count(*)
            """,
            (day_start.timestamp(), next_day.timestamp()),
        )
        [count] = cur.fetchone()

    logger.info(f"Deleted {count} events for {day.isoformat()}")
