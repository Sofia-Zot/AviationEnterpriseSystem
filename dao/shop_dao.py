from typing import List, Optional
import psycopg2
from db.connection import DatabaseConnection
from models.shop import Shop
from dao.base_dao import BaseDAO


class ShopDAO(BaseDAO[Shop]):
    def get_all(self) -> List[Shop]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id_shop, name FROM shop ORDER BY id_shop"
                )
                rows = cur.fetchall()
                return [Shop(id_shop=row[0], name=row[1]) for row in rows]
        except psycopg2.Error as e:
            print(f"Ошибка при получении списка цехов: {e}")
            return []
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def get_by_id(self, id: int) -> Optional[Shop]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id_shop, name FROM shop WHERE id_shop = %s",
                    (id,),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                return Shop(id_shop=row[0], name=row[1])
        except psycopg2.Error as e:
            print(f"Ошибка при получении цеха по ID: {e}")
            return None
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def insert(self, entity: Shop) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO shop (name)
                    VALUES (%s)
                    RETURNING id_shop
                    """,
                    (entity.name,),
                )
                row = cur.fetchone()
                if row:
                    entity.id_shop = row[0]
                conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Ошибка при добавлении цеха: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def update(self, entity: Shop) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE shop SET name = %s WHERE id_shop = %s",
                    (entity.name, entity.id_shop),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при обновлении цеха: {e}")
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
                    "DELETE FROM shop WHERE id_shop = %s",
                    (id,),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при удалении цеха: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)
