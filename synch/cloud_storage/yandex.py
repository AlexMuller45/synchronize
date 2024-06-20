import requests
from requests import HTTPError, Timeout, RequestException

from synch.core.config import config
from synch.core.log_config import logger
from handle_errors import handle_errors


class YandexDisk:
    api_host: str = "cloud-api.yandex.net"
    api_version: str = "/v1"
    api_disk: str = "/disk"
    api_resources: str = "/resources"
    api_timeout: int = 10

    def __init__(self):
        self.api_main_url: str = (f"{self.api_host}/"
                                  f"{self.api_version}/"
                                  f"{self.api_disk}/"
                                  f"{self.api_resources}")
        self.oauth_token: str | None = config.get("yandex_disk_token", None)
        self.headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"OAuth {self.oauth_token}",
        }
        self.api_get_info_url: str = (f"{self.api_main_url}"
                                      f"?path={config.get("path_cloud_folder")}"
                                      f"&fields={config.get("yandex_disk_fields")}")

    def upload(self, file_path: str): ...

    def reload(self, file_path: str): ...

    def delete(self, file_name: str): ...

    @handle_errors
    def get_info(self) -> dict[str, list[dict]] | None:
        response = requests.get(
            self.api_get_info_url,
            headers=self.headers,
            timeout=self.api_timeout,
            )
        response.raise_for_status()

        return response.json()["_embedded"]
