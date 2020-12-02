import json
import os
from datetime import date, datetime, timedelta, timezone
from io import StringIO
from unittest import TestCase

import psycopg2

from .archiver import create_day_archive


class TestArchiver(TestCase):
    def setUp(self):
        db_url = os.getenv("DATABASE_URL", "postgres://")
        self.conn = psycopg2.connect(db_url)
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
        timestamp=datetime(2020, 12, 2, 14, 5, 2).timestamp(),
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

    def test_create_day_archive(self):
        """
        Should write line separated json into the provided file, from the data in the
        events database
        """
        self.create_event(
            timestamp=datetime(2020, 12, 3, tzinfo=timezone.utc).timestamp()
        )
        self.create_event(
            timestamp=(
                datetime(2020, 12, 2, tzinfo=timezone.utc) - timedelta(seconds=1)
            ).timestamp()
        )
        for _ in range(2):
            self.create_event()
        file = StringIO()
        create_day_archive(self.conn, file, date(2020, 12, 2))
        file.seek(0)
        lines = file.readlines()
        self.assertEqual(len(lines), 2)
        for i, line in enumerate(lines):
            self.assertEqual(
                json.loads(line),
                {
                    "id": i + 3,
                    "sender_id": "27820001001",
                    "type_name": "action",
                    "timestamp": 1606910702,
                    "intent_name": None,
                    "action_name": "action_session_start",
                    "data": '{"event": "session_started"}',
                },
            )
