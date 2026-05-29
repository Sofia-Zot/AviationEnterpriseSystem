import sys
import logging
import traceback
import os

from PyQt5.QtWidgets import QApplication, QMessageBox

from db.connection import DatabaseConnection
from services.auth_service import AuthService
from dao.query_dao import QueryDAO
from gui.login_window import LoginWindow
from gui.main_window import MainWindow
from utils.logger import get_logger

# Настраиваем базовое логирование в app.log (корень проекта)
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)

logger = get_logger()


def main():
    """Точка входа приложения."""
    app = QApplication(sys.argv)

    try:
        logger.info("Запуск AviationEnterpriseSystem")

        # Инициализация подключения к БД
        db = DatabaseConnection()
        auth_service = AuthService(db)
        query_dao = QueryDAO(db)

        logger.info("Подключение к базе данных успешно")

        # Окно авторизации
        login_window = LoginWindow(auth_service)

        if login_window.exec_() == LoginWindow.Accepted:
            user = login_window.get_user()
            if user:
                logger.info("Пользователь авторизован: %s (роль: %s)", user.login, user.role)
                # Главное окно (передаём query_dao)
                main_window = MainWindow(user, query_dao)
                main_window.show()
                return app.exec_()
            else:
                logger.warning("Не удалось получить данные пользователя")
                QMessageBox.critical(None, "Ошибка", "Не удалось получить данные пользователя")
                return 1
        else:
            # Пользователь отменил вход
            logger.info("Пользователь отменил вход")
            return 0

    except Exception as e:
        logger.exception("Критическая ошибка при запуске: %s", str(e))
        print(f"\nПолный traceback:\n{traceback.format_exc()}")
        QMessageBox.critical(None, "Критическая ошибка", f"{str(e)}\n\n{traceback.format_exc()}")
        return 1
    finally:
        # Закрытие соединений с БД
        try:
            db = DatabaseConnection()
            db.close_all_connections()
            logger.info("Соединения с БД закрыты")
        except Exception as e:
            logger.error("Ошибка при закрытии соединений: %s", str(e))


if __name__ == "__main__":
    sys.exit(main())