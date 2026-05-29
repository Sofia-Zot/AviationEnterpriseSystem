"""
Скрипт для заполнения базы данных демо-данными.
"""

import configparser
import psycopg2
from psycopg2 import sql

# Читаем настройки из config.ini
config = configparser.ConfigParser()
config.read('db/config.ini', encoding='utf-8')

DB_CONFIG = {
    'host': config.get('database', 'host'),
    'database': config.get('database', 'dbname'),
    'user': config.get('database', 'user'),
    'password': config.get('database', 'password'),
    'port': config.getint('database', 'port')
}

print("INFO: Настройки БД: {0}".format(DB_CONFIG))

def execute_seed_script():
    """Читает и выполняет seed_data.sql"""
    try:
        # Читаем SQL-скрипт
        with open('db/seed_data.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Подключаемся к БД
        print("INFO: Подключение к БД...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        cur = conn.cursor()
        
        try:
            # Выполняем скрипт
            print("OK: Выполнение скрипта seed_data.sql...")
            cur.execute(sql_script)
            conn.commit()
            print("OK: Демо-данные успешно загружены!")

            # Показываем статистику
            print("\n--- Статистика данных ---")
            tables = [
                ('shop', 'Цехов'),
                ('laboratory', 'Лабораторий'),
                ('product_category', 'Категорий продукции'),
                ('employee', 'Сотрудников'),
                ('section', 'Участков'),
                ('brigade', 'Бригад'),
                ('worker', 'Рабочих'),
                ('engineer', 'ИТР'),
                ('tester', 'Испытателей'),
                ('product_type', 'Видов изделий'),
                ('product_instance', 'Изделий'),
                ('work_execution', 'Работ (выполнение)'),
                ('test_execution', 'Испытаний (выполнение)'),
            ]
            
            for table, desc in tables:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                print("  OK: {0} - {1}".format(count, desc))

        except Exception as e:
            conn.rollback()
            print("ERR: Ошибка при выполнении: {0}".format(e))
            raise
        finally:
            cur.close()
            conn.close()
            
    except FileNotFoundError:
        print("ERR: Файл db/seed_data.sql не найден!")
    except Exception as e:
        print("ERR: Ошибка: {0}".format(e))

if __name__ == "__main__":
    execute_seed_script()
