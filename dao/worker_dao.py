from typing import List, Optional
import psycopg2
from db.connection import DatabaseConnection
from models.worker import Worker
from dao.base_dao import BaseDAO


class WorkerDAO(BaseDAO[Worker]):
    def get_all(self) -> List[Worker]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id_employee, profession, rank, is_foreman, id_brigade
                    FROM worker
                    ORDER BY id_employee
                    """
                )
                rows = cur.fetchall()
                return [
                    Worker(
                        id_employee=row[0],
                        profession=row[1],
                        rank=row[2],
                        is_foreman=row[3],
                        id_brigade=row[4],
                    )
                    for row in rows
                ]
        except psycopg2.Error as e:
            print(f"Ошибка при получении списка рабочих: {e}")
            return []
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def get_by_id(self, id: int) -> Optional[Worker]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id_employee, profession, rank, is_foreman, id_brigade
                    FROM worker
                    WHERE id_employee = %s
                    """,
                    (id,),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                return Worker(
                    id_employee=row[0],
                    profession=row[1],
                    rank=row[2],
                    is_foreman=row[3],
                    id_brigade=row[4],
                )
        except psycopg2.Error as e:
            print(f"Ошибка при получении рабочего по ID: {e}")
            return None
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def insert(self, entity: Worker) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO worker (id_employee, profession, rank, is_foreman, id_brigade)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        entity.id_employee,
                        entity.profession,
                        entity.rank,
                        entity.is_foreman,
                        entity.id_brigade,
                    ),
                )
                conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Ошибка при добавлении рабочего: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def update(self, entity: Worker) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE worker
                    SET profession = %s, rank = %s, is_foreman = %s, id_brigade = %s
                    WHERE id_employee = %s
                    """,
                    (
                        entity.profession,
                        entity.rank,
                        entity.is_foreman,
                        entity.id_brigade,
                        entity.id_employee,
                    ),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при обновлении рабочего: {e}")
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
                    "DELETE FROM worker WHERE id_employee = %s",
                    (id,),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при удалении рабочего: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)
