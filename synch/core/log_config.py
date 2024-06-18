import datetime
import os
import sys
from loguru import logger as loguru_logger
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent


class MyLogger:
    def __init__(self):
        self.logger = loguru_logger.bind(app_name="synchronizer")
        self.logger.add(
            sys.stderr,
            format="{extra[app_name]} {time:YYYY-MM-DD HH:mm:ss.SSS} {level: <8} {message}",
            level="DEBUG",
        )
        self.logger.add(
            get_log_filename(),
            format="{extra[app_name]} {time:YYYY-MM-DD HH:mm:ss.SSS} {level: <8} {message}",
            level="DEBUG",
        )

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
    dirname = f"{BASE_DIR}/logs"

    if not os.path.isdir(dirname):
        os.mkdir(dirname)

    return f"{dirname}/log_{now.strftime("%Y_%m_%d")}.log"


logger = MyLogger()
