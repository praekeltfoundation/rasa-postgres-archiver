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


## Configuration
The following env vars are provided for configuration:

`DATABASE` - url describing how to connect to the database

`S3_BUCKET` - the bucket to upload the archives to

`AWS_ACCESS_KEY_ID` - the access key for the AWS account

`AWS_SECRET_ACCESS_KEY` - the secret key for the AWS account

`S3_KEY_PREFIX` - the prefix to add to S3 keys, defaults to "events", which will create keys like "events-2020-12-02.json.gz"

`LOGLEVEL` - The level to log at. Defaults to INFO

`S3_REGION` - The S3 region name.
