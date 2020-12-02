# Rasa PostgreSQL archiver

** Not yet complete **

For the Rasa PostgreSQL tracker store, this can take older data, archive it to S3, and then delete it from the database.

This will ensure that the database does not grow indefinitely.


## Running tests
PostgreSQL is required. Defaults to connecting to a local postgreSQL instance, but
can be configured using the DATABASE_URL environment variable

Install the requirements

```bash
~ pip install -r requirements.txt -r requirements-dev.txt
```

Run the unit tests
```bash
~ python -m unittest
```

Run the auto linting
```bash
~ black .
~ isort .
~ flake8
```
