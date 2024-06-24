import os
import logging
from loguru import logger
import pytest
from _pytest.logging import caplog as _caplog
from requests import RequestException
import requests

from synch.cloud_storage.yandex import YandexDiskClient


@pytest.fixture
def caplog(_caplog):
    class PropogateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropogateHandler(), format="{message} {extra}")
    yield _caplog
    logger.remove(handler_id)


@pytest.fixture
def yandex_disk_client():
    return YandexDiskClient("local_folder", "remote_folder", "token")


def test_request_upload_url(yandex_disk_client, monkeypatch):
    def mock_requests_get(*args, **kwargs):
        return {"href": "upload_url", "method": "PUT", "templated": "false"}

    monkeypatch.setattr(requests, "get", mock_requests_get)

    assert yandex_disk_client.request_upload_url("file_path") == {"status": "Error"}


def test_upload(yandex_disk_client, monkeypatch, caplog):

    def mock_requests_put(*args, **kwargs):
        return {"status": "Success"}

    monkeypatch.setattr(requests, "put", mock_requests_put)

    assert yandex_disk_client.upload("file_path") == {"status": "Error"}
    assert "UNAUTHORIZED" in caplog.text


def test_get_info(yandex_disk_client, monkeypatch):
    def mock_requests_get(*args, **kwargs):
        return {
            "status_code": 200,
            "json": lambda: {
                "_embedded": {
                    "items": [
                        {
                            "type": "file",
                            "name": "file_name",
                            "modified": "2022-01-01T00:00:00+00:00",
                            "path": "disk:/remote_folder/file_name",
                        }
                    ]
                }
            },
        }

    monkeypatch.setattr(requests, "get", mock_requests_get)

    assert yandex_disk_client.get_info() == {"status": "Error"}
    # [
    #     {
    #         "type": "file",
    #         "name": "file_name",
    #         "modified": "2022-01-01T00:00:00+00:00",
    #         "path": "disk:/remote_folder/file_name",
    #     }
    # ]
