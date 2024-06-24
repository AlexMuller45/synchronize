from datetime import datetime
import os
import time

from cloud_storage import YandexDiskClient
from core.config import config
from core.log_config import logger


class Synchronizer:
    def __init__(self):
        self.local_path: str = str(config.get("path_local_folder", ""))
        self.remote_path: str = str(config.get("path_cloud_folder", ""))
        self.cloud_token: str = str(config.get("yandex_oauth_token", ""))
        self.delay: int = int(str(config.get("synch_delay", "30")))
        self.running: bool = False
        self.cloud_drive = YandexDiskClient(
            local_folder=self.local_path,
            remote_folder=self.remote_path,
            token=self.cloud_token,
        )
        logger.info(f"remote_path: {self.remote_path}")

    def __get_mtime_iso8601(self, file_name: str) -> str:
        # 2014-04-22T10:32:49+04:00

        full_path = os.path.join(self.local_path, file_name)
        mtime_struct = time.gmtime(os.path.getmtime(full_path))

        return time.strftime("%Y-%m-%dT%H:%M:%S%z", mtime_struct)

    def __get_local_files_with_mtime(self) -> list[dict]:
        list_dir = os.listdir(self.local_path)
        return [
            {
                "name": item,
                "modified": self.__get_mtime_iso8601(item),
                "path": os.path.join(self.local_path, item),
                "type": "file",
            }
            for item in list_dir
            if os.path.isfile(os.path.join(self.local_path, item))
        ]

    @staticmethod
    def __find_name_in_remote_files(
        name: str,
        remote_files: list[dict],
    ) -> dict | None:
        return next((item for item in remote_files if item.get("name") == name), None)

    @staticmethod
    def __remove_remote_file_by_name(name, remote_files) -> list[dict]:
        return [{**item} for item in remote_files if item.get("name") != name]

    def sync_files(self):

        local_files: list[dict] = self.__get_local_files_with_mtime()
        logger.info(
            "Локальные файлы для синхронизации: "
            f"{[item["name"] for item in local_files]}"
        )

        remote_files: list[dict] = self.cloud_drive.get_info()
        logger.info(f"Файлы в облаке: {[item["name"] for item in remote_files]}")

        for file in local_files:
            remote_file: dict | None = self.__find_name_in_remote_files(
                file["name"],
                remote_files,
            )
            file_name: str = file.get("name") or ""

            if remote_file:
                mtime_local_file = datetime.fromisoformat(file["modified"])
                mtime_remote_file = datetime.fromisoformat(remote_file["modified"])

                if mtime_local_file > mtime_remote_file:
                    logger.info(f"Обновление файла {file_name} в облаке")
                    self.cloud_drive.reload(file_name)

                remote_files = self.__remove_remote_file_by_name(
                    file_name,
                    remote_files,
                )

            else:
                logger.info(f"Загрузка файла {file_name} в облако")
                self.cloud_drive.upload(file_name)

        if remote_files:
            for file in remote_files:
                remote_file_name = file.get("name")
                if remote_file_name:
                    logger.info(f"Удаление файла {remote_file_name} из облака")
                    self.cloud_drive.delete(str(remote_file_name))

        logger.info("Синхронизация завершена")

    def stop_sync(self):
        logger.info("Синхронизация остановлена")
        self.running = False

    def start_sync(self):
        self.running = True
        try:
            while self.running:
                logger.info("Синхронизация запущена")
                self.sync_files()
                time.sleep(self.delay)

        except KeyboardInterrupt:
            self.stop_sync()
