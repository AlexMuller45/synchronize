from core.config import config
from core.log_config import logger
from utils.synchronize import Synchronizer


if __name__ == "__main__":
    logger.info("Начало работы программы синхронизации!!!")
    logger.info(
        "Запуск синхронизации директории"
        f"{config.get("path_local_folder", "директория не определена")}"
    )

    sync_files = Synchronizer()

    try:
        sync_files.start_sync()
    except KeyboardInterrupt:
        sync_files.stop_sync()
