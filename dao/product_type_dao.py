from typing import List, Optional
import psycopg2
from db.connection import DatabaseConnection
from models.product_type import ProductType
from dao.base_dao import BaseDAO


class ProductTypeDAO(BaseDAO[ProductType]):
    def get_all(self) -> List[ProductType]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id_type, name, id_category
                    FROM product_type
                    ORDER BY id_type
                    """
                )
                rows = cur.fetchall()
                return [
                    ProductType(
                        id_type=row[0],
                        name=row[1],
                        id_category=row[2],
                    )
                    for row in rows
                ]
        except psycopg2.Error as e:
            print(f"Ошибка при получении списка типов изделий: {e}")
            return []
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def get_all_with_relations(self) -> List[ProductType]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        pt.id_type,
                        pt.name,
                        pt.id_category,
                        pc.name AS category_name
                    FROM product_type pt
                    JOIN product_category pc ON pt.id_category = pc.id_category
                    ORDER BY pt.id_type
                """)
                rows = cur.fetchall()
                return [
                    ProductType(
                        id_type=row[0],
                        name=row[1],
                        id_category=row[2],
                        category_name=row[3],
                    )
                    for row in rows
                ]
        except psycopg2.Error as e:
            print(f"Ошибка при получении списка типов изделий: {e}")
            return []
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def get_by_id(self, id: int) -> Optional[ProductType]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id_type, name, id_category
                    FROM product_type
                    WHERE id_type = %s
                    """,
                    (id,),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                return ProductType(
                    id_type=row[0],
                    name=row[1],
                    id_category=row[2],
                )
        except psycopg2.Error as e:
            print(f"Ошибка при получении типа изделия по ID: {e}")
            return None
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def insert(self, entity: ProductType) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO product_type (name, id_category)
                    VALUES (%s, %s)
                    RETURNING id_type
                    """,
                    (entity.name, entity.id_category),
                )
                row = cur.fetchone()
                if row:
                    entity.id_type = row[0]
                conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Ошибка при добавлении типа изделия: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def update(self, entity: ProductType) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE product_type
                    SET name = %s, id_category = %s
                    WHERE id_type = %s
                    """,
                    (
                        entity.name,
                        entity.id_category,
                        entity.id_type,
                    ),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при обновлении типа изделия: {e}")
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
                # Сначала удаляем записи из таблиц подтипов
                cur.execute("DELETE FROM aircraft_type WHERE id_type = %s", (id,))
                cur.execute("DELETE FROM rocket_type WHERE id_type = %s", (id,))
                cur.execute("DELETE FROM glider_type WHERE id_type = %s", (id,))
                cur.execute("DELETE FROM helicopter_type WHERE id_type = %s", (id,))
                cur.execute("DELETE FROM hangglider_type WHERE id_type = %s", (id,))
                cur.execute("DELETE FROM other_type WHERE id_type = %s", (id,))

                # Затем удаляем основную запись
                cur.execute(
                    "DELETE FROM product_type WHERE id_type = %s",
                    (id,),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при удалении типа изделия: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)
