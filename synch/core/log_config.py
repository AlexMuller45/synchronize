import datetime
import os
import sys
from loguru import logger as loguru_logger
from pathlib import Path

from config import config


BASE_DIR = Path(__file__).parent.parent.parent


class MyLogger:
    def __init__(self):
        self.logger = loguru_logger
        self.logger.remove()

        self.logger.add(
            sys.stderr,
            format="{extra[app_name]} {time:YYYY-MM-DD HH:mm:ss.SSS} {level} {message}",
            level="DEBUG",
        )
        self.logger.add(
            get_log_filename(),
            retention="15 days",
            format="{extra[app_name]} {time:YYYY-MM-DD HH:mm:ss.SSS} {level} {message}",
            level="DEBUG",
        )

        self.logger = self.logger.bind(app_name="synchronizer")

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)


def get_log_filename():
    now = datetime.datetime.now()
    log_path = config.get("path_local_log", "")
    dirname = f"{BASE_DIR}{log_path}"

    if not os.path.isdir(dirname):
        os.mkdir(dirname)

    return f"{dirname}/log_{now.strftime("%Y_%m_%d")}.log"


logger = MyLogger()
