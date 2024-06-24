from requests.exceptions import HTTPError, Timeout, RequestException

from core.log_config import logger


def handle_errors(func):
    """
    Функция handle_errors - это декоратор, который обрабатывает исключения
        HTTPError, Timeout и RequestException.
        Внутри декоратора создается обертка, которая вызывает функцию func
        и обрабатывает исключения. Если возникает исключение HTTPError,
        Timeout или RequestException, возвращается словарь
        с ключом "status" и значением "Error". В противном случае,
        функция func вызывается и ее результат возвращается.
    """

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
        return {"status": "Error"}

    return wrapper
