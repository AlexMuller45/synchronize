from datetime import datetime
import os
import time

from cloud_storage import YandexDiskClient
from core.config import config
from core.log_config import logger


class Synchronizer:
    """
    Класс Synchronizer представляет собой синхронизатор файлов
        между локальной папкой и облаком.
    В методе __init__ инициализируются переменные,
        такие как local_path, remote_path, cloud_token и delay.
        Также создается экземпляр класса YandexClient.
    Метод __get_mtime_iso8601 возвращает время последнего изменения файла
        в формате ISO 8601.
    Метод __get_local_files_with_mtime возвращает список словарей,
        где каждый словарь содержит информацию о файле в локальной папке.
    Метод __find_name_in_remote_files ищет файл с заданным именем
        в списке файлов в облаке.
    Метод __remove_remote_file_by_name удаляет файл с заданным именем
        из списка файлов в облаке.
    Метод sync_files синхронизирует файлы между локальной папкой и облаком.
    Метод stop_sync останавливает синхронизацию.
    Метод start_sync запускает синхронизацию.
    """

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
        try:
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

        except FileNotFoundError as err:
            logger.error(f"Путь {self.local_path} не найден: {err}")

        except Exception as e:
            logger.error(f"Ошибка при получении списка файлов: {e}")

        return []

    @staticmethod
    def __find_name_in_remote_files(
        name: str,
        remote_files: list[dict],
    ) -> dict | None:
        return next((item for item in remote_files if item.get("name") == name), None)

    def sync_files(self):

        local_files: list[dict] = self.__get_local_files_with_mtime()
        logger.info(
            "Локальные файлы для синхронизации: "
            f"{[item["name"] for item in local_files]}"
        )

        remote_files: list[dict] = self.cloud_drive.get_info()

        if remote_files is None:
            logger.error("данные из облака не получены")
            return

        logger.info(
            f"Имеющиеся файлы в облаке: {[item["name"] for item in remote_files]}"
        )

        remote_files_dict = {file["name"]: file for file in remote_files}

        for file in local_files:
            file_name: str = file.get("name", "")
            if not file_name:
                continue

            remote_file = remote_files_dict.pop(file_name, None)
            mtime_local_file = datetime.fromisoformat(file["modified"])

            if remote_file:
                mtime_remote_file = datetime.fromisoformat(remote_file["modified"])

                if mtime_local_file > mtime_remote_file:
                    logger.info(f"Обновление файла {file_name} в облаке")
                    self.cloud_drive.reload(file_name)

            else:
                logger.info(f"Загрузка файла {file_name} в облако")
                self.cloud_drive.upload(file_name)

        for remote_file_name in remote_files_dict.keys():
            logger.info(f"Удаление файла {remote_file_name} из облака")
            self.cloud_drive.delete(remote_file_name)

        logger.info("Синхронизация завершена")

    def stop_sync(self):
        logger.info("Синхронизация остановлена")
        self.running = False

    def start_sync(self):
        self.running = True
        counter = 0
        try:
            while self.running:
                counter += 1
                logger.info("Синхронизация запущена")
                self.sync_files()

                for remaining in range(self.delay, 0, -1):
                    print(f"....ожидание {remaining} сек.", end="\r")
                    time.sleep(1)

        except KeyboardInterrupt:
            self.stop_sync()
