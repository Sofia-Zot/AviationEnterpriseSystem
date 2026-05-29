
import logging
import os
from datetime import datetime


def setup_logger(name='aviation_app', log_file=None):
    """
    Настраивает логгер с выводом в консоль и/или файл.

    Args:
        name: Имя логгера
        log_file: Путь к файлу логов (если None - только консоль)

    Returns:
        logging.Logger: Настроенный логгер
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Формат сообщения
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Файловый обработчик (если указан)
    if log_file:
        # Создаём директорию логов, если не существует
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Создаём глобальный логгер
logger = setup_logger(
    name='aviation_app',
    log_file='logs/app.log'
)


def get_logger():
    """Возвращает глобальный логгер."""
    return logger
