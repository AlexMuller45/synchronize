import os
import requests
from requests import RequestException
from urllib.parse import quote

from synch.core.log_config import logger
from synch.cloud_storage.handle_errors import handle_errors


class YandexApiUrl:
    timeout: int = 10
    host: str = "https://cloud-api.yandex.net"
    version: str = "/v1"
    disk: str = "/disk"
    resources: str = "/resources"
    upload: str = "/upload"
    fields: str = (
        "_embedded.items.type,_embedded.items.name,"
        "_embedded.items.path,_embedded.items.modified"
    )
    permanently: str = "false"

    def __init__(self):
        self.main_url: str = f"{self.host}{self.version}{self.disk}{self.resources}"

    @staticmethod
    def encode_path(path: str | None) -> str:
        return quote(path) if path else ""

    def get_info_url(self, remote_path: str) -> str:
        encoded_path = self.encode_path(remote_path)
        return f"{self.main_url}?path={encoded_path}&fields={self.fields}"

    def get_upload_url(self, file_path: str, upload: bool = False) -> str:
        overwrite: str = "true" if upload else "false"
        encoded_path = self.encode_path(file_path)
        return (
            f"{self.main_url}{self.upload}"
            f"?path={encoded_path}"
            f"&overwrite={overwrite}"
        )

    def get_delete_url(self, file_name: str, remote_path: str) -> str:
        full_path = os.path.join(remote_path, file_name)
        encoded_path = self.encode_path(full_path)
        return (
            f"{self.main_url}?path={encoded_path}"
            f"&force_async=false&permanently={self.permanently}"
        )


class YandexDiskClient:
    api: YandexApiUrl = YandexApiUrl()

    def __init__(self, local_folder: str, remote_folder: str, token: str):
        self.oauth_token: str = token
        self.remote_path: str = remote_folder
        self.local_path: str = local_folder
        self.headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"OAuth {token}",
        }

    @handle_errors
    def request_upload_url(self, file_path: str, upload: bool = False) -> str | None:

        response = requests.get(
            self.api.get_upload_url(file_path, upload),
            headers=self.headers,
            timeout=self.api.timeout,
        )

        if response.status_code == 200:
            return response.json()["href"]

        if response.status_code == 409:
            logger.error(
                f"Файл уже существует, ответ сервера: {response.json()["message"]}"
            )
            return None

        response.raise_for_status()

    @handle_errors
    def upload(self, file_path: str) -> dict[str, str]:
        upload_url = self.request_upload_url(file_path=file_path)

        if not upload_url:
            raise RequestException("URL для загрузки не получен")

        with open(file_path, "rb") as file:
            response = requests.put(upload_url, data=file)

        response.raise_for_status()

        logger.info(f"Файл {file_path} загружен успешно")
        return {"status": "Success"}

    @handle_errors
    def reload(self, file_path: str) -> dict[str, str]:
        reload_url = self.request_upload_url(
            file_path=file_path,
            upload=True,
        )

        if not reload_url:
            raise RequestException("URL для загрузки не получен")

        with open(file_path, "rb") as file:
            response = requests.put(
                reload_url,
                data=file,
            )
        response.raise_for_status()

        logger.info(f"Файл {file_path} заменен успешно")
        return {"status": "Success"}

    @handle_errors
    def delete(self, file_name: str):
        delete_url = self.api.get_delete_url(file_name, self.remote_path)
        response = requests.delete(
            delete_url,
            headers=self.headers,
            timeout=self.api.timeout,
        )

        response.raise_for_status()

        logger.info(f"Файл {file_name} удален")
        return {"status": "Success"}

    @staticmethod
    def remove_dir(items: list[dict]) -> list[dict]:
        return [{**item} for item in items if item["type"] == "file"]

    @handle_errors
    def get_info(self) -> list[dict]:
        # returns list[dict]:
        # [
        #     "name": "bar-2.sdf"
        #     "modified": "2014-04-22T10:32:49+04:00"
        #     "path": "disk:/foo/bar-2.sdf"
        #     "type": "file"
        # ]

        response = requests.get(
            self.api.get_info_url(self.remote_path),
            headers=self.headers,
            timeout=self.api.timeout,
        )
        response.raise_for_status()

        data: list[dict] = response.json()["_embedded"]["items"]

        return self.remove_dir(data)
