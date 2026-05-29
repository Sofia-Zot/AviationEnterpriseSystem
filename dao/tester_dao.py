
from typing import List, Optional
import psycopg2
from db.connection import DatabaseConnection
from models.tester import Tester
from dao.base_dao import BaseDAO


class TesterDAO(BaseDAO[Tester]):
    def get_all(self) -> List[Tester]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id_employee, id_lab, specialization
                    FROM tester
                    ORDER BY id_employee
                    """
                )
                rows = cur.fetchall()
                return [
                    Tester(
                        id_employee=row[0],
                        id_lab=row[1],
                        specialization=row[2],
                    )
                    for row in rows
                ]
        except psycopg2.Error as e:
            print(f"Ошибка при получении списка испытателей: {e}")
            return []
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def get_by_id(self, id: int) -> Optional[Tester]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id_employee, id_lab, specialization
                    FROM tester
                    WHERE id_employee = %s
                    """,
                    (id,),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                return Tester(
                    id_employee=row[0],
                    id_lab=row[1],
                    specialization=row[2],
                )
        except psycopg2.Error as e:
            print(f"Ошибка при получении испытателя по ID: {e}")
            return None
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def insert(self, entity: Tester) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO tester (id_employee, id_lab, specialization)
                    VALUES (%s, %s, %s)
                    """,
                    (
                        entity.id_employee,
                        entity.id_lab,
                        entity.specialization,
                    ),
                )
                conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Ошибка при добавлении испытателя: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def update(self, entity: Tester) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE tester
                    SET id_lab = %s, specialization = %s
                    WHERE id_employee = %s
                    """,
                    (
                        entity.id_lab,
                        entity.specialization,
                        entity.id_employee,
                    ),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при обновлении испытателя: {e}")
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
                    "DELETE FROM tester WHERE id_employee = %s",
                    (id,),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при удалении испытателя: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)
