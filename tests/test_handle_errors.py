import logging
import pytest
from _pytest.logging import caplog as _caplog
from loguru import logger
from requests import HTTPError, RequestException, Timeout

from synch.cloud_storage.handle_errors import handle_errors


@pytest.fixture
def caplog(_caplog):
    class PropogateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropogateHandler(), format="{message} {extra}")
    yield _caplog
    logger.remove(handler_id)


@handle_errors
def sample_handle_errors():
    raise HTTPError("Пример HTTP-ошибки")


@handle_errors
def sample_timeout_function():
    raise Timeout("Пример ошибки timeout error")


@handle_errors
def sample_request_exception_function():
    raise RequestException("Пример исключения request")


@handle_errors
def sample_generic_exception_function():
    raise Exception("Пример общего исключения")


def test_handle_errors_http_error(caplog):
    result = sample_handle_errors()
    assert result == {"status": "Error"}
    assert "Возникла HTTP ошибка: Пример HTTP-ошибки" in caplog.text


def test_handle_errors_timeout_error(caplog):
    result = sample_timeout_function()
    assert result == {"status": "Error"}
    assert "Превышено время ожидания ответа: Пример ошибки timeout error" in caplog.text


def test_handle_errors_request_exception(caplog):
    result = sample_request_exception_function()
    assert result == {"status": "Error"}
    assert "Ошибка запроса: Пример исключения request" in caplog.text


def test_handle_errors_generic_exception(caplog):
    result = sample_generic_exception_function()
    assert result == {"status": "Error"}
    assert "Ошибка: Пример общего исключения" in caplog.text
