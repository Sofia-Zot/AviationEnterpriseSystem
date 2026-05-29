from typing import Optional
import psycopg2

from db.connection import DatabaseConnection
from models.user import User
from utils.password_hasher import hash_password, verify_password


class AuthService:


    def __init__(self, db: DatabaseConnection):
        """
        Args:
            db: Экземпляр DatabaseConnection для получения соединений из пула.
        """
        self.db = db

    def authenticate(self, login: str, password: str) -> Optional[User]:
        """
        Проверяет логин и пароль, возвращает объект User при успехе.

        Args:
            login: Логин пользователя.
            password: Пароль в открытом виде.

        Returns:
            User: Объект пользователя при успешной аутентификации.
            None: Если пользователь не найден или пароль неверный.
        """
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT login, password_hash, role, id_employee
                    FROM users
                    WHERE login = %s
                    """,
                    (login,),
                )
                row = cur.fetchone()
                if row is None:
                    return None

                _, password_hash, role, id_employee = row
                if verify_password(password, password_hash):
                    return User(
                        login=login,
                        password_hash=password_hash,
                        role=role,
                        id_employee=id_employee,
                    )
                return None
        except psycopg2.Error as e:
            print(f"Ошибка аутентификации: {e}")
            return None
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def get_user_by_login(self, login: str) -> Optional[User]:
        """
        Получает данные пользователя по логину (без проверки пароля).

        Args:
            login: Логин пользователя.

        Returns:
            User: Объект пользователя или None если не найден.
        """
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT login, password_hash, role, id_employee
                    FROM users
                    WHERE login = %s
                    """,
                    (login,),
                )
                row = cur.fetchone()
                if row is None:
                    return None

                return User(
                    login=row[0],
                    password_hash=row[1],
                    role=row[2],
                    id_employee=row[3],
                )
        except psycopg2.Error as e:
            print(f"Ошибка получения пользователя: {e}")
            return None
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def create_user(
        self,
        login: str,
        password: str,
        role: str,
        id_employee: Optional[int] = None,
    ) -> bool:
        """
        Создаёт нового пользователя.

        Args:
            login: Логин пользователя.
            password: Пароль в открытом виде (будет захеширован).
            role: Роль пользователя.
            id_employee: ID сотрудника (опционально).

        Returns:
            bool: True если успешно, False если ошибка или пользователь существует.
        """
        conn = None
        try:
            conn = self.db.get_connection()
            password_hash = hash_password(password)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (login, password_hash, role, id_employee)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (login, password_hash, role, id_employee),
                )
                conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Ошибка создания пользователя: {e}")
            if conn is not None:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def change_password(self, login: str, new_password: str) -> bool:
        """
        Меняет пароль пользователя.

        Args:
            login: Логин пользователя.
            new_password: Новый пароль.

        Returns:
            bool: True если успешно, False если ошибка.
        """
        conn = None
        try:
            conn = self.db.get_connection()
            password_hash = hash_password(new_password)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE users
                    SET password_hash = %s
                    WHERE login = %s
                    """,
                    (password_hash, login),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка смены пароля: {e}")
            if conn is not None:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def delete_user(self, login: str) -> bool:
        """
        Удаляет пользователя.

        Args:
            login: Логин пользователя.

        Returns:
            bool: True если успешно удалён, False если ошибка или не найден.
        """
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM users
                    WHERE login = %s
                    """,
                    (login,),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка удаления пользователя: {e}")
            if conn is not None:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                self.db.return_connection(conn)
