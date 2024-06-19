class YandexDisk:
    api_host: str = "cloud-api.yandex.net"
    api_version: str = "v1"

    def __init__(self):
        self.api_url: str = f"{self.api_host}/{self.api_version}/"

    def upload(self, file_path: str): ...

    def reload(self, file_path: str): ...

    def delete(self, file_name: str): ...

    def get_info(self): ...
