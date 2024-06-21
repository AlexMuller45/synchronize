from core.config import config
from core.log_config import logger


def main() -> None:
    return print("hi")


if __name__ == "__main__":
    logger.info("Начало работы программы синхронизации!!!")
    logger.info(
        "Запуск синхронизации директории"
        f"{config.get("path_local_folder", "директория не определена")}"
    )

    main()
