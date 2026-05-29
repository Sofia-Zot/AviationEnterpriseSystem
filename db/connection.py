import configparser
import psycopg2
from psycopg2 import pool
import os


class DatabaseConnection:
    """
    Синглтон-класс для управления подключением к базе данных PostgreSQL.
    Использует пул соединений для эффективного управления ресурсами.
    """
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        """Создает единственный экземпляр класса (синглтон)"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Инициализирует соединение при первом создании экземпляра"""
        if DatabaseConnection._pool is None:
            self._config = self._load_config()
            DatabaseConnection._pool = self._create_pool()
    
    def _load_config(self):
        """
        Читает конфигурацию базы данных из файла config.ini.
        Возвращает: dict: Параметры подключения (host, port, dbname, user, password)
        """
        config = configparser.ConfigParser()
        
        # Определяем путь к config.ini относительно этого файла
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, 'config.ini')
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"Файл конфигурации не найден: {config_path}. "
                "Скопируйте db/config.ini.example в db/config.ini и настройте параметры."
            )
        
        config.read(config_path, encoding='utf-8')
        
        return {
            'host': config.get('database', 'host'),
            'port': config.getint('database', 'port'),
            'dbname': config.get('database', 'dbname'),
            'user': config.get('database', 'user'),
            'password': config.get('database', 'password')
        }
    
    def _create_pool(self):
        """
        Создает пул соединений к базе данных.
        Возвращает:  SimpleConnectionPool: Пул соединений psycopg2
        """
        return pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=self._config['host'],
            port=self._config['port'],
            database=self._config['dbname'],
            user=self._config['user'],
            password=self._config['password']
        )
    
    def get_connection(self):
        """
        Возвращает соединение из пула.
        Возвращает: connection: Соединение с базой данных
        """
        if DatabaseConnection._pool is None:
            raise RuntimeError("Пул соединений не инициализирован")
        return DatabaseConnection._pool.getconn()
    
    def return_connection(self, conn):
        """
        Возвращает соединение в пул.
        Args: conn: Соединение с базой данных для возврата в пул
        """
        if DatabaseConnection._pool is not None:
            DatabaseConnection._pool.putconn(conn)
    
    def close_all_connections(self):
        """Закрывает все соединения в пуле."""
        if DatabaseConnection._pool is not None:
            DatabaseConnection._pool.closeall()
            DatabaseConnection._pool = None
