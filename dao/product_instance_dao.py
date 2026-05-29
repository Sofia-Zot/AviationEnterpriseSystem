from typing import List, Optional
import psycopg2
from db.connection import DatabaseConnection
from models.product_instance import ProductInstance
from dao.base_dao import BaseDAO


class ProductInstanceDAO(BaseDAO[ProductInstance]):
    def get_all(self) -> List[ProductInstance]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT serial_number, status, id_shop, id_type,
                           weight, material, batch
                    FROM product_instance
                    ORDER BY serial_number
                    """
                )
                rows = cur.fetchall()
                return [
                    ProductInstance(
                        serial_number=row[0],
                        status=row[1],
                        id_shop=row[2],
                        id_type=row[3],
                        weight=row[4],
                        material=row[5],
                        batch=row[6],
                    )
                    for row in rows
                ]
        except psycopg2.Error as e:
            print(f"Ошибка при получении списка изделий: {e}")
            return []
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def get_all_with_relations(self) -> List[ProductInstance]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        pi.serial_number,
                        pi.status,
                        pi.id_shop,
                        pi.id_type,
                        pi.weight,
                        pi.material,
                        pi.batch,
                        pt.name AS product_type_name,
                        pc.name AS product_category_name,
                        sh.name AS shop_name
                    FROM product_instance pi
                    JOIN product_type pt ON pi.id_type = pt.id_type
                    JOIN product_category pc ON pt.id_category = pc.id_category
                    JOIN shop sh ON pi.id_shop = sh.id_shop
                    ORDER BY pi.serial_number
                """)
                rows = cur.fetchall()
                return [
                    ProductInstance(
                        serial_number=row[0],
                        status=row[1],
                        id_shop=row[2],
                        id_type=row[3],
                        weight=row[4],
                        material=row[5],
                        batch=row[6],
                        product_type_name=row[7],
                        product_category_name=row[8],
                        shop_name=row[9],
                    )
                    for row in rows
                ]
        except psycopg2.Error as e:
            print(f"Ошибка при получении списка изделий: {e}")
            return []
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def get_by_id(self, id: int) -> Optional[ProductInstance]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT serial_number, status, id_shop, id_type,
                           weight, material, batch
                    FROM product_instance
                    WHERE serial_number = %s
                    """,
                    (id,),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                return ProductInstance(
                    serial_number=row[0],
                    status=row[1],
                    id_shop=row[2],
                    id_type=row[3],
                    weight=row[4],
                    material=row[5],
                    batch=row[6],
                )
        except psycopg2.Error as e:
            print(f"Ошибка при получении изделия по ID: {e}")
            return None
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def insert(self, entity: ProductInstance) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO product_instance (
                        serial_number, status, id_shop, id_type,
                        weight, material, batch
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        entity.serial_number,
                        entity.status,
                        entity.id_shop,
                        entity.id_type,
                        entity.weight,
                        entity.material,
                        entity.batch,
                    ),
                )
                conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Ошибка при добавлении изделия: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def update(self, entity: ProductInstance) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE product_instance
                    SET status = %s, id_shop = %s, id_type = %s,
                        weight = %s, material = %s, batch = %s
                    WHERE serial_number = %s
                    """,
                    (
                        entity.status,
                        entity.id_shop,
                        entity.id_type,
                        entity.weight,
                        entity.material,
                        entity.batch,
                        entity.serial_number,
                    ),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при обновлении изделия: {e}")
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
                # Удаляем записи из таблиц подтипов (явно, хотя есть ON DELETE CASCADE)
                cur.execute("DELETE FROM aircraft_instance WHERE serial_number = %s", (id,))
                cur.execute("DELETE FROM rocket_instance WHERE serial_number = %s", (id,))
                cur.execute("DELETE FROM glider_instance WHERE serial_number = %s", (id,))
                cur.execute("DELETE FROM helicopter_instance WHERE serial_number = %s", (id,))
                cur.execute("DELETE FROM hangglider_instance WHERE serial_number = %s", (id,))
                cur.execute("DELETE FROM other_instance WHERE serial_number = %s", (id,))

                # Удаляем основную запись
                cur.execute(
                    "DELETE FROM product_instance WHERE serial_number = %s",
                    (id,),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при удалении изделия: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)
