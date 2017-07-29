import os
import logging

DEBUG = os.environ.get("DEBUG", True)
LOG_LEVEL = logging.INFO

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite://")
CREATE_ENGINE = {
    "encoding": 'utf-8',
    "pool_recycle": 3600,
    "echo": DEBUG,
}

SLACK_URL = os.environ.get("SLACK_URL")

DATE_FORMATS = ["%Y/%m/%d", "%Y-%m-%d"]
