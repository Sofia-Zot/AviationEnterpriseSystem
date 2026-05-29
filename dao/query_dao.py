from datetime import date
from typing import List, Tuple, Optional
import psycopg2

from db.connection import DatabaseConnection


class QueryDAO:
    def __init__(self, db: DatabaseConnection):
        self.db = db

    def _fetch_all(self, cursor) -> List[dict]:
        """Преобразует результат курсора в список словарей."""
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def query1_product_types(
        self, shop_id: Optional[int] = None, category_id: Optional[int] = None
    ) -> List[str]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT DISTINCT product_type_name
                    FROM view_product_types_by_shop
                    WHERE (id_shop = %s OR %s IS NULL)
                      AND (id_category = %s OR %s IS NULL)
                    ORDER BY product_type_name
                    """,
                    (shop_id, shop_id, category_id, category_id),
                )
                return [row[0] for row in cur.fetchall()]
        except psycopg2.Error as e:
            print(f"Ошибка в query1_product_types: {e}")
            return []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query2_completed_products(
        self,
        shop_id: Optional[int] = None,
        category_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Tuple[int, List[dict]]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM view_completed_products
                    WHERE (id_shop = %s OR %s IS NULL)
                      AND (id_category = %s OR %s IS NULL)
                      AND (completion_date >= %s OR %s IS NULL)
                      AND (completion_date <= %s OR %s IS NULL)
                    ORDER BY completion_date
                    """,
                    (shop_id, shop_id, category_id, category_id,
                     start_date, start_date, end_date, end_date),
                )
                rows = self._fetch_all(cur)
                return len(rows), rows
        except psycopg2.Error as e:
            print(f"Ошибка в query2_completed_products: {e}")
            return 0, []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query3_workers(
        self, shop_id: Optional[int] = None, section_id: Optional[int] = None
    ) -> List[dict]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM view_workers
                    WHERE (id_shop = %s OR %s IS NULL)
                      AND (id_section = %s OR %s IS NULL)
                    ORDER BY last_name, first_name
                    """,
                    (shop_id, shop_id, section_id, section_id),
                )
                return self._fetch_all(cur)
        except psycopg2.Error as e:
            print(f"Ошибка в query3_workers: {e}")
            return []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query3_engineers(
        self, category: Optional[str] = None
    ) -> List[dict]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM view_engineers
                    WHERE (category = %s OR %s IS NULL)
                    ORDER BY last_name, first_name
                    """,
                    (category, category),
                )
                return self._fetch_all(cur)
        except psycopg2.Error as e:
            print(f"Ошибка в query3_engineers: {e}")
            return []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query4_sections_with_managers(
        self, shop_id: Optional[int] = None
    ) -> List[dict]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM view_sections_with_managers
                    WHERE (id_shop = %s OR %s IS NULL)
                    ORDER BY id_section
                    """,
                    (shop_id, shop_id),
                )
                return self._fetch_all(cur)
        except psycopg2.Error as e:
            print(f"Ошибка в query4_sections_with_managers: {e}")
            return []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query5_work_steps(self, serial_number: int) -> List[dict]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT work_name, step_number, execution_status,
                           start_date, end_date, section_name
                    FROM view_product_work_steps
                    WHERE serial_number = %s
                    ORDER BY step_number
                    """,
                    (serial_number,),
                )
                return self._fetch_all(cur)
        except psycopg2.Error as e:
            print(f"Ошибка в query5_work_steps: {e}")
            return []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query6_brigade_members(
        self,
        brigade_id: Optional[int] = None,
        section_id: Optional[int] = None,
        shop_id: Optional[int] = None,
    ) -> List[dict]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM view_brigade_members
                    WHERE (id_brigade = %s OR %s IS NULL)
                      AND (id_section = %s OR %s IS NULL)
                      AND (id_shop = %s OR %s IS NULL)
                    ORDER BY brigade_name, last_name
                    """,
                    (brigade_id, brigade_id, section_id, section_id,
                     shop_id, shop_id),
                )
                return self._fetch_all(cur)
        except psycopg2.Error as e:
            print(f"Ошибка в query6_brigade_members: {e}")
            return []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query7_masters(
        self, shop_id: Optional[int] = None, section_id: Optional[int] = None
    ) -> List[dict]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM view_masters ORDER BY last_name")
                return self._fetch_all(cur)
        except psycopg2.Error as e:
            print(f"Ошибка в query7_masters: {e}")
            return []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query8_products_in_assembly(
        self, shop_id: Optional[int] = None, category_id: Optional[int] = None
    ) -> List[dict]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT serial_number, product_type_name, shop_name
                    FROM view_products_in_assembly
                    WHERE (id_shop = %s OR %s IS NULL)
                      AND (id_category = %s OR %s IS NULL)
                    ORDER BY serial_number
                    """,
                    (shop_id, shop_id, category_id, category_id),
                )
                return self._fetch_all(cur)
        except psycopg2.Error as e:
            print(f"Ошибка в query8_products_in_assembly: {e}")
            return []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query9_brigades_for_product(self, serial_number: int) -> List[dict]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT DISTINCT brigade_name, section_name,
                                    last_name, first_name, profession
                    FROM view_brigades_for_product
                    WHERE serial_number = %s
                    ORDER BY brigade_name, last_name
                    """,
                    (serial_number,),
                )
                return self._fetch_all(cur)
        except psycopg2.Error as e:
            print(f"Ошибка в query9_brigades_for_product: {e}")
            return []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query10_labs_for_product(self, serial_number: int) -> List[dict]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT lab_name, lab_type
                    FROM view_labs_for_product
                    WHERE serial_number = %s
                    ORDER BY lab_name
                    """,
                    (serial_number,),
                )
                return self._fetch_all(cur)
        except psycopg2.Error as e:
            print(f"Ошибка в query10_labs_for_product: {e}")
            return []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query11_tested_products(
        self,
        lab_id: Optional[int] = None,
        category_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[dict]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM view_tested_products
                    WHERE (id_lab = %s OR %s IS NULL)
                      AND (id_category = %s OR %s IS NULL)
                      AND (test_date >= %s OR %s IS NULL)
                      AND (test_date <= %s OR %s IS NULL)
                    ORDER BY test_date
                    """,
                    (lab_id, lab_id, category_id, category_id,
                     start_date, start_date, end_date, end_date),
                )
                return self._fetch_all(cur)
        except psycopg2.Error as e:
            print(f"Ошибка в query11_tested_products: {e}")
            return []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query12_testers(
        self,
        serial_number: Optional[int] = None,
        category_id: Optional[int] = None,
        lab_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[dict]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT DISTINCT last_name, first_name, specialization
                    FROM view_testers
                    WHERE (serial_number = %s OR %s IS NULL)
                      AND (id_category = %s OR %s IS NULL)
                      AND (id_lab = %s OR %s IS NULL)
                      AND (test_date >= %s OR %s IS NULL)
                      AND (test_date <= %s OR %s IS NULL)
                    ORDER BY last_name, first_name
                    """,
                    (serial_number, serial_number, category_id, category_id,
                     lab_id, lab_id, start_date, start_date,
                     end_date, end_date),
                )
                return self._fetch_all(cur)
        except psycopg2.Error as e:
            print(f"Ошибка в query12_testers: {e}")
            return []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query13_equipment_for_tests(
        self,
        serial_number: Optional[int] = None,
        lab_id: Optional[int] = None,
    ) -> List[dict]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT DISTINCT equipment_name, equipment_model
                    FROM view_equipment_for_tests
                    WHERE (serial_number = %s OR %s IS NULL)
                      AND (id_lab = %s OR %s IS NULL)
                    ORDER BY equipment_name
                    """,
                    (serial_number, serial_number, lab_id, lab_id),
                )
                return self._fetch_all(cur)
        except psycopg2.Error as e:
            print(f"Ошибка в query13_equipment_for_tests: {e}")
            return []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query14_assembly_summary(
        self,
        shop_id: Optional[int] = None,
        section_id: Optional[int] = None,
    ) -> Tuple[int, List[dict]]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COALESCE(SUM(product_count), 0)
                    FROM view_products_in_assembly_summary
                    WHERE (id_shop = %s OR %s IS NULL)
                      AND (id_section = %s OR %s IS NULL)
                    """,
                    (shop_id, shop_id, section_id, section_id),
                )
                total = cur.fetchone()[0] or 0

                cur.execute(
                    """
                    SELECT * FROM view_products_in_assembly_summary
                    WHERE (id_shop = %s OR %s IS NULL)
                      AND (id_section = %s OR %s IS NULL)
                    ORDER BY shop_name, section_name, category_name
                    """,
                    (shop_id, shop_id, section_id, section_id),
                )
                rows = self._fetch_all(cur)
                return total, rows
        except psycopg2.Error as e:
            print(f"Ошибка в query14_assembly_summary: {e}")
            return 0, []
        finally:
            if conn is not None:
                self.db.return_connection(conn)