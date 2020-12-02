from datetime import datetime, timedelta, timezone


def create_day_archive(conn, file, day):
    """
    Creates an archive for the specified day, using UTC
    conn: postgresql connection
    file: file object to write output to
    day: datetime.date of the day the archive is for
    """
    day_start = datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc)
    next_day = day_start + timedelta(days=1)

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
            file.write(row[0])
            file.write("\n")
