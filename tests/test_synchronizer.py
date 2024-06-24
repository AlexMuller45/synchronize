import os
import time
import pytest
from synch.cloud_storage.yandex import YandexDiskClient
from synch.core.config import config
from synch.core.log_config import logger
from synch.utils.synchronize import Synchronizer


@pytest.fixture
def synchronizer():
    return Synchronizer()


def test_init(synchronizer):
    assert synchronizer.local_path == str(config.get("path_local_folder", ""))
    assert synchronizer.remote_path == str(config.get("path_cloud_folder", ""))
    assert synchronizer.cloud_token == str(config.get("yandex_oauth_token", ""))
    assert synchronizer.delay == int(str(config.get("synch_delay", "30")))


def test_find_name_in_remote_files(synchronizer):
    remote_files = [
        {
            "name": "file1",
            "modified": "2022-01-25T10:32:49+00:00",
            "path": "full_path",
            "type": "file",
        },
        {
            "name": "file2",
            "modified": "2022-11-25T10:32:49+00:00",
            "path": "full_path",
            "type": "file",
        },
    ]
    assert synchronizer._Synchronizer__find_name_in_remote_files(
        "file1", remote_files
    ) == {
        "name": "file1",
        "modified": "2022-01-25T10:32:49+00:00",
        "path": "full_path",
        "type": "file",
    }


def test_remove_remote_file_by_name(synchronizer):
    remote_files = [
        {
            "name": "file1",
            "modified": "2022-01-25T10:32:49+00:00",
            "path": "full_path",
            "type": "file",
        },
        {
            "name": "file2",
            "modified": "2022-01-25T10:32:49+00:00",
            "path": "full_path",
            "type": "file",
        },
    ]
    assert synchronizer._Synchronizer__remove_remote_file_by_name(
        "file1", remote_files
    ) == [
        {
            "name": "file2",
            "modified": "2022-01-25T10:32:49+00:00",
            "path": "full_path",
            "type": "file",
        }
    ]


def test_sync_files(synchronizer, monkeypatch):
    def mock_get_info(*args):
        return [
            {
                "name": "file1",
                "modified": "2022-01-25T10:32:49+00:00",
                "path": "full_path",
                "type": "file",
            }
        ]

    def mock_reload(*args):
        pass

    def mock_upload(*args):
        pass

    def mock_delete(*args):
        pass

    monkeypatch.setattr(synchronizer.cloud_drive, "get_info", mock_get_info)
    monkeypatch.setattr(synchronizer.cloud_drive, "reload", mock_reload)
    monkeypatch.setattr(synchronizer.cloud_drive, "upload", mock_upload)
    monkeypatch.setattr(synchronizer.cloud_drive, "delete", mock_delete)

    synchronizer.sync_files()

