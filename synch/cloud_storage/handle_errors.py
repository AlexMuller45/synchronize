from requests import HTTPError, Timeout, RequestException

from synch.core.log_config import logger


def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPError as http_err:
            logger.error(f"Возникла HTTP ошибка: {http_err}")
        except Timeout as timeout_err:
            logger.error(f"Превышено время ожидания ответа: {timeout_err}")
        except RequestException as req_err:
            logger.error(f"Ошибка запроса: {req_err}")
        except Exception as err:
            logger.error(f"Ошибка: {err}")
        return None

    return wrapper
