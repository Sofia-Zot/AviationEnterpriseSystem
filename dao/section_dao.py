from typing import List, Optional
import psycopg2
from db.connection import DatabaseConnection
from models.section import Section
from dao.base_dao import BaseDAO


class SectionDAO(BaseDAO[Section]):
    def get_all(self) -> List[Section]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id_section, name, id_shop FROM section ORDER BY id_section"
                )
                rows = cur.fetchall()
                return [
                    Section(id_section=row[0], name=row[1], id_shop=row[2])
                    for row in rows
                ]
        except psycopg2.Error as e:
            print(f"Ошибка при получении списка участков: {e}")
            return []
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def get_by_id(self, id: int) -> Optional[Section]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id_section, name, id_shop FROM section WHERE id_section = %s",
                    (id,),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                return Section(id_section=row[0], name=row[1], id_shop=row[2])
        except psycopg2.Error as e:
            print(f"Ошибка при получении участка по ID: {e}")
            return None
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def insert(self, entity: Section) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO section (name, id_shop)
                    VALUES (%s, %s)
                    RETURNING id_section
                    """,
                    (entity.name, entity.id_shop),
                )
                row = cur.fetchone()
                if row:
                    entity.id_section = row[0]
                conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Ошибка при добавлении участка: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def update(self, entity: Section) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE section SET name = %s, id_shop = %s WHERE id_section = %s",
                    (entity.name, entity.id_shop, entity.id_section),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при обновлении участка: {e}")
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
                    "DELETE FROM section WHERE id_section = %s",
                    (id,),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при удалении участка: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)
