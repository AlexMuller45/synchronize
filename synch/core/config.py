from dotenv import dotenv_values, find_dotenv

from log_config import logger


if not find_dotenv():
    logger.error("Файл с переменными .env не найден")
    exit()

config = dotenv_values(".env")
