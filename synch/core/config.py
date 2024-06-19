from dotenv import dotenv_values, find_dotenv
from collections import OrderedDict

from log_config import logger


if not find_dotenv():
    logger.error("Файл с переменными .env не найден")
    exit()

config = OrderedDict(
    (k.lower(), v) for k, v in dotenv_values(".env", encoding="utf-8").items()
)

print(config)
