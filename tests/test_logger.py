import pytest
from unittest.mock import patch, MagicMock
import datetime
import os
import tempfile
from pathlib import Path
from loguru import logger as loguru_logger

from synch.core.log_config import (
    MyLogger,
    get_log_filename,
)

BASE_DIR = Path(__file__).parent.parent + "\synch"

@pytest.fixture
def mock_base_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        original_base_dir = BASE_DIR
        BASE_DIR = Path(tmpdirname)
        yield BASE_DIR
        BASE_DIR = original_base_dir


def test_get_log_filename(mock_base_dir):
    now = datetime.datetime.now()
    expected_dir = mock_base_dir / "logs"
    expected_filename = f"{expected_dir}/log_{now.strftime('%Y_%m_%d')}.log"

    with patch("your_module.datetime") as mock_datetime:
        mock_datetime.datetime.now.return_value = now
        log_filename = get_log_filename()

        assert log_filename == str(expected_filename)
        assert os.path.isdir(expected_dir)


@pytest.fixture
def mock_logger(mocker):
    mock_logger = mocker.patch("your_module.loguru_logger")
    return mock_logger


def test_mylogger_initialization(mock_logger, mock_base_dir):
    logger = MyLogger()
    assert logger.logger is not None
    assert mock_logger.bind.called
    assert mock_logger.add.call_count == 2


def test_mylogger_methods(mock_logger):
    logger = MyLogger()

    logger.debug("debug message")
    logger.logger.debug.assert_called_once_with("debug message")

    logger.info("info message")
    logger.logger.info.assert_called_once_with("info message")

    logger.warning("warning message")
    logger.logger.warning.assert_called_once_with("warning message")

    logger.error("error message")
    logger.logger.error.assert_called_once_with("error message")

    logger.critical("critical message")
    logger.logger.critical.assert_called_once_with("critical message")


if __name__ == "__main__":
    pytest.main()
