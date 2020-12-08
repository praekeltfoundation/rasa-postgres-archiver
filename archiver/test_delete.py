from datetime import date, datetime, timedelta, timezone
from unittest import TestCase, mock

import boto3
import psycopg2
from moto import mock_s3

from archiver import settings
from archiver.delete import delete_day, delete_events


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
        """
        Deletes events that fall on the specified day
        """
        self.create_event()
        self.create_event(
            timestamp=datetime(2020, 12, 3, 14, 5, 2, tzinfo=timezone.utc).timestamp()
        )
        delete_day(self.conn, date(2020, 12, 2))
        with self.conn.cursor() as cur:
            cur.execute("SELECT count(*) from events")
            [count] = cur.fetchone()
            self.assertEqual(count, 1)

    @mock_s3
    @mock.patch("archiver.delete.date")
    def test_delete_events(self, date_mock):
        """
        Deletes all events that we have archives for within time range
        """
        # We can't mock date.today, we have to mock the whole datetime module
        # but we still need date.fromisoformat, so we put that back
        date_mock.today.return_value = date(2020, 12, 3) + timedelta(days=30)
        date_mock.fromisoformat = date.fromisoformat
        self.create_event()
        self.create_event(
            timestamp=datetime(2020, 12, 3, 14, 5, 2, tzinfo=timezone.utc).timestamp()
        )

        client = boto3.resource("s3")
        bucket = client.create_bucket(Bucket="rasa-archive")
        bucket.put_object(Key="events-2020-12-02.json.gz")

        delete_events(self.conn, bucket)

        with self.conn.cursor() as cur:
            cur.execute("SELECT count(*) from events")
            [count] = cur.fetchone()
            self.assertEqual(count, 1)
