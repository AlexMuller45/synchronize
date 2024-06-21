import requests
from requests import HTTPError, Timeout, RequestException

from synch.core.config import config
from synch.core.log_config import logger
from handle_errors import handle_errors


class YandexApiUrl:
    timeout: int = 10
    host: str = "cloud-api.yandex.net"
    version: str = "/v1"
    disk: str = "/disk"
    resources: str = "/resources"
    upload: str = "/upload"

    def __init__(self):
        self.main_url: str = (
            f"{self.host}/" f"{self.version}/" f"{self.disk}/" f"{self.resources}"
        )

    def get_info_url(self) -> str:
        return (
            f"{self.main_url}"
            f"?path={config.get("path_cloud_folder")}"
            f"&fields={config.get("yandex_disk_fields")}"
        )

    def get_upload_url(self, upload: bool = False) -> str:
        overwrite: str = "false"
        if upload:
            overwrite: str = "true"
        return f"{self.main_url}{self.upload}" "?path={}" f"&overwrite={overwrite}"


class YandexDisk:
    api: YandexApiUrl = YandexApiUrl()

    def __init__(self):
        self.oauth_token: str | None = config.get("yandex_disk_token", None)
        self.headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"OAuth {self.oauth_token}",
        }

    @handle_errors
    def request_upload_url(self, upload: bool = False) -> str | None:

        response = requests.get(
            self.api.get_upload_url(upload),
            headers=self.headers,
            timeout=self.api.timeout,
        )

        if response.status_code == 200:  # 409
            return response.json()["href"]

        if response.status_code == 409:
            logger.error(f"Файл уже существует, ошибка: {response.json()["message"]}")
            return None

        response.raise_for_status()

    @handle_errors
    def upload(self, file_path: str) -> dict[str, str]:
        upload_url = self.request_upload_url()
        if not upload_url:
            logger.error("Ошибка загрузки файла")
            return {"status": "Error"}

        with open(file_path, "rb") as file:
            response = requests.put(
                upload_url,
                data=file,
            )
        response.raise_for_status()

        logger.info(f"Файл {file_path} загружен успешно")
        return {"status": "Success"}

    @handle_errors
    def reload(self, file_path: str) -> dict[str, str]:
        reload_url = self.request_upload_url(upload=True)
        if not reload_url:
            return {"status": "Error"}

        with open(file_path, "rb") as file:
            response = requests.put(
                reload_url,
                data=file,
            )
        response.raise_for_status()

        logger.info(f"Файл {file_path} заменен успешно")
        return {"status": "Success"}

    @handle_errors
    def delete(self, file_name: str): ...

    @handle_errors
    def get_info(self) -> dict[str, list[dict]] | None:
        response = requests.get(
            self.api.get_info_url(),
            headers=self.headers,
            timeout=self.api.timeout,
        )
        response.raise_for_status()

        return response.json()["_embedded"]
