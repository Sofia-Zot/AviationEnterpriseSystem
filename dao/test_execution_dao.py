
from typing import List, Optional
import psycopg2
from db.connection import DatabaseConnection
from models.test_execution import TestExecution
from dao.base_dao import BaseDAO


class TestExecutionDAO(BaseDAO[TestExecution]):
    def get_all(self) -> List[TestExecution]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT te.id_test_execution, te.serial_number, te.id_test_step,
                           te.start_date, te.end_date, te.result,
                           twl.test_name as test_step_name
                    FROM test_execution te
                    LEFT JOIN test_step ts ON te.id_test_step = ts.id_step
                    LEFT JOIN test_work_list twl ON ts.id_test_work = twl.id_test_work
                    ORDER BY te.id_test_execution
                    """
                )
                rows = cur.fetchall()
                result = []
                for row in rows:
                    result.append(TestExecution(
                        id_test_execution=row[0],
                        serial_number=row[1],
                        id_test_step=row[2],
                        date_start=row[3],
                        date_end=row[4],
                        result=row[5],
                        test_step_name=row[6],
                    ))
                return result
        except psycopg2.Error as e:
            print(f"Ошибка при получении списка испытаний: {e}")
            return []
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def get_by_id(self, id: int) -> Optional[TestExecution]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id_test_execution, serial_number, id_test_step,
                           start_date, end_date, result
                    FROM test_execution
                    WHERE id_test_execution = %s
                    """,
                    (id,),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                return TestExecution(
                    id_test_execution=row[0],
                    serial_number=row[1],
                    id_test_step=row[2],
                    date_start=row[3],
                    date_end=row[4],
                    result=row[5],
                )
        except psycopg2.Error as e:
            print(f"Ошибка при получении испытания по ID: {e}")
            return None
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def insert(self, entity: TestExecution) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO test_execution (
                        serial_number, id_test_step, start_date, end_date, result
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id_test_execution
                    """,
                    (
                        entity.serial_number,
                        entity.id_test_step,
                        entity.date_start,
                        entity.date_end,
                        entity.result,
                    ),
                )
                row = cur.fetchone()
                if row:
                    entity.id_test_execution = row[0]
                conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Ошибка при добавлении испытания: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def update(self, entity: TestExecution) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE test_execution
                    SET serial_number = %s, id_test_step = %s,
                        start_date = %s, end_date = %s, result = %s
                    WHERE id_test_execution = %s
                    """,
                    (
                        entity.serial_number,
                        entity.id_test_step,
                        entity.date_start,
                        entity.date_end,
                        entity.result,
                        entity.id_test_execution,
                    ),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при обновлении испытания: {e}")
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
                    "DELETE FROM test_execution WHERE id_test_execution = %s",
                    (id,),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при удалении испытания: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)
