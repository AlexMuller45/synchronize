import os
import time

from synch.cloud_storage import YandexDiskClient
from synch.core.config import config


class Synchronizer:
    def __init__(self):
        self.local_path: str = str(config.get("path_local_folder", ""))
        self.remote_path: str = str(config.get("path_cloud_folder", ""))
        self.cloud_token: str = str(config.get("yandex_oauth_token", ""))

        self.cloud_drive = YandexDiskClient(
            local_folder=self.local_path,
            remote_folder=self.remote_path,
            token=self.cloud_token,
        )

    def get_mtime_iso8601(self, file_name: str) -> str:
        # 2014-04-22T10:32:49+04:00

        full_path = os.path.join(self.local_path, file_name)
        mtime_struct = time.gmtime(os.path.getmtime(full_path))

        return time.strftime("%Y-%m-%dT%H:%M:%S%z", mtime_struct)

    def get_local_files_with_mtime(self) -> list[tuple[str, str]]:
        list_dir = os.listdir(self.local_path)

        return [
            (item, self.get_mtime_iso8601(item))
            for item in list_dir
            if os.path.isfile(item)
        ]

    def sync_folders(self):
        pass
