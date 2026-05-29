from typing import List, Optional
import psycopg2
from db.connection import DatabaseConnection
from models.engineer import Engineer
from dao.base_dao import BaseDAO


class EngineerDAO(BaseDAO[Engineer]):
    def get_all(self) -> List[Engineer]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id_employee, category, position
                    FROM engineer
                    ORDER BY id_employee
                    """
                )
                rows = cur.fetchall()
                return [
                    Engineer(
                        id_employee=row[0],
                        category=row[1],
                        position=row[2],
                    )
                    for row in rows
                ]
        except psycopg2.Error as e:
            print(f"Ошибка при получении списка инженеров: {e}")
            return []
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def get_by_id(self, id: int) -> Optional[Engineer]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id_employee, category, position
                    FROM engineer
                    WHERE id_employee = %s
                    """,
                    (id,),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                return Engineer(
                    id_employee=row[0],
                    category=row[1],
                    position=row[2],
                )
        except psycopg2.Error as e:
            print(f"Ошибка при получении инженера по ID: {e}")
            return None
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def insert(self, entity: Engineer) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO engineer (id_employee, category, position)
                    VALUES (%s, %s, %s)
                    """,
                    (
                        entity.id_employee,
                        entity.category,
                        entity.position,
                    ),
                )
                conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Ошибка при добавлении инженера: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def update(self, entity: Engineer) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE engineer
                    SET category = %s, position = %s
                    WHERE id_employee = %s
                    """,
                    (
                        entity.category,
                        entity.position,
                        entity.id_employee,
                    ),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при обновлении инженера: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def delete(self, id: int) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM engineer WHERE id_employee = %s",
                    (id,),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при удалении инженера: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)
