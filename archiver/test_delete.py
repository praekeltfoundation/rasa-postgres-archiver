from datetime import date, datetime, timezone
from unittest import TestCase

import psycopg2

from archiver import settings
from archiver.delete import delete_day


class TestArchiver(TestCase):
    def setUp(self):
        self.conn = psycopg2.connect(settings.DATABASE)
        with self.conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE events(
                    id serial PRIMARY KEY NOT NULL,
                    sender_id character varying(255) NOT NULL,
                    type_name character varying(255) NOT NULL,
                    "timestamp" double precision,
                    intent_name character varying(255),
                    action_name character varying(255),
                    data text
                )"""
            )

    def tearDown(self):
        self.conn.rollback()
        self.conn.close()

    def create_event(
        self,
        sender_id="27820001001",
        type_name="action",
        timestamp=datetime(2020, 12, 2, 14, 5, 2, tzinfo=timezone.utc).timestamp(),
        intent_name=None,
        action_name="action_session_start",
        data='{"event": "session_started"}',
    ):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO events(sender_id, type_name, timestamp, intent_name,
                    action_name, data)
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (sender_id, type_name, timestamp, intent_name, action_name, data),
            )

    def test_delete_day(self):
        self.create_event()
        self.create_event(
            timestamp=datetime(2020, 12, 3, 14, 5, 2, tzinfo=timezone.utc).timestamp()
        )
        delete_day(self.conn, date(2020, 12, 2))
        with self.conn.cursor() as cur:
            cur.execute("SELECT count(*) from events")
            [count] = cur.fetchone()
            self.assertEqual(count, 1)
