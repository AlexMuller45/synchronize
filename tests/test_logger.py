import datetime
import os
import random
import string
from pathlib import Path


from synch.core.log_config import (
    get_log_filename,
    logger,
)


BASE_DIR = Path(__file__).parent.parent / "synch"


def get_key(length: int) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def test_get_log_filename():
    now = datetime.datetime.now()
    expected_filename = f"{BASE_DIR}/logs/log_{now.strftime('%Y_%m_%d')}.log"
    assert get_log_filename() == expected_filename


def test_logger_info():
    test_message = f"{get_key(8)} Тестовое сообщение"
    logger.info(test_message)
    assert os.path.exists(get_log_filename())
    with open(get_log_filename(), "r") as f:
        log_content = f.read()
        assert f"INFO {test_message}" in log_content


def test_logger_warning():
    test_message = f"{get_key(8)} Тестовое сообщение"
    logger.warning(test_message)
    assert os.path.exists(get_log_filename())
    with open(get_log_filename(), "r") as f:
        log_content = f.read()
        assert f"WARNING {test_message}" in log_content


def test_logger_error():
    test_message = f"{get_key(8)} Тестовое сообщение"
    logger.error(test_message)
    assert os.path.exists(get_log_filename())
    with open(get_log_filename(), "r") as f:
        log_content = f.read()
        assert f"ERROR {test_message}" in log_content


def test_logger_critical():
    test_message = f"{get_key(8)} Тестовое сообщение"
    logger.critical(test_message)
    assert os.path.exists(get_log_filename())
    with open(get_log_filename(), "r") as f:
        log_content = f.read()
        assert f"CRITICAL {test_message}" in log_content
