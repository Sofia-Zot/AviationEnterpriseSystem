from typing import List, Optional
import psycopg2
from db.connection import DatabaseConnection
from models.brigade import Brigade
from dao.base_dao import BaseDAO


class BrigadeDAO(BaseDAO[Brigade]):
    def get_all(self) -> List[Brigade]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id_brigade, name, id_section, id_foreman
                    FROM brigade
                    ORDER BY id_brigade
                    """
                )
                rows = cur.fetchall()
                return [
                    Brigade(
                        id_brigade=row[0],
                        name=row[1],
                        id_section=row[2],
                        id_foreman=row[3],
                    )
                    for row in rows
                ]
        except psycopg2.Error as e:
            print(f"Ошибка при получении списка бригад: {e}")
            return []
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def get_all_with_relations(self) -> List[Brigade]:
        """
        Возвращает бригады с названиями участков, цехов и бригадиров.
        """
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        b.id_brigade,
                        b.name,
                        b.id_section,
                        b.id_foreman,
                        sec.name AS section_name,
                        sh.name AS shop_name,
                        CONCAT(e.last_name, ' ', e.first_name) AS foreman_name
                    FROM brigade b
                    JOIN section sec ON b.id_section = sec.id_section
                    JOIN shop sh ON sec.id_shop = sh.id_shop
                    LEFT JOIN employee e ON b.id_foreman = e.id_employee
                    ORDER BY b.id_brigade
                """)
                rows = cur.fetchall()
                return [
                    Brigade(
                        id_brigade=row[0],
                        name=row[1],
                        id_section=row[2],
                        id_foreman=row[3],
                        section_name=row[4],
                        shop_name=row[5],
                        foreman_name=row[6],
                    )
                    for row in rows
                ]
        except psycopg2.Error as e:
            print(f"Ошибка при получении списка бригад: {e}")
            return []
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def get_by_id(self, id: int) -> Optional[Brigade]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id_brigade, name, id_section, id_foreman
                    FROM brigade
                    WHERE id_brigade = %s
                    """,
                    (id,),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                return Brigade(
                    id_brigade=row[0],
                    name=row[1],
                    id_section=row[2],
                    id_foreman=row[3],
                )
        except psycopg2.Error as e:
            print(f"Ошибка при получении бригады по ID: {e}")
            return None
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def insert(self, entity: Brigade) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO brigade (name, id_section, id_foreman)
                    VALUES (%s, %s, %s)
                    RETURNING id_brigade
                    """,
                    (entity.name, entity.id_section, entity.id_foreman),
                )
                row = cur.fetchone()
                if row:
                    entity.id_brigade = row[0]
                conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Ошибка при добавлении бригады: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def update(self, entity: Brigade) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE brigade
                    SET name = %s, id_section = %s, id_foreman = %s
                    WHERE id_brigade = %s
                    """,
                    (
                        entity.name,
                        entity.id_section,
                        entity.id_foreman,
                        entity.id_brigade,
                    ),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при обновлении бригады: {e}")
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
                # Сначала удаляем рабочих бригады (чтобы не нарушить FK)
                cur.execute("DELETE FROM worker WHERE id_brigade = %s", (id,))
                # Затем удаляем саму бригаду
                cur.execute(
                    "DELETE FROM brigade WHERE id_brigade = %s",
                    (id,),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при удалении бригады: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)
