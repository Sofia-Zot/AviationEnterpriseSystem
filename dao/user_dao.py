from typing import Optional, List
import psycopg2

from db.connection import DatabaseConnection
from models.user import User


class UserDAO:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def get_by_login(self, login: str) -> Optional[User]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT login, password_hash, role, id_employee FROM users WHERE login = %s",
                    (login,),
                )
                row = cur.fetchone()
                if row:
                    return User(login=row[0], password_hash=row[1], role=row[2], id_employee=row[3])
                return None
        except psycopg2.Error as e:
            print(f"Ошибка UserDAO.get_by_login: {e}")
            return None
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def get_all(self) -> List[User]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT login, password_hash, role, id_employee FROM users ORDER BY login")
                return [User(login=r[0], password_hash=r[1], role=r[2], id_employee=r[3]) for r in cur.fetchall()]
        except psycopg2.Error as e:
            print(f"Ошибка UserDAO.get_all: {e}")
            return []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def insert(self, login: str, password_hash: str, role: str, id_employee: Optional[int] = None) -> bool:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (login, password_hash, role, id_employee) VALUES (%s, %s, %s, %s)",
                    (login, password_hash, role, id_employee),
                )
                conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Ошибка UserDAO.insert: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def update_password(self, login: str, new_password_hash: str) -> bool:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET password_hash = %s WHERE login = %s",
                    (new_password_hash, login),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка UserDAO.update_password: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def delete(self, login: str) -> bool:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE login = %s", (login,))
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка UserDAO.delete: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                self.db.return_connection(conn)
