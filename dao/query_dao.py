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
                    SELECT DISTINCT pt.name AS product_type_name
                    FROM product_type pt
                    JOIN product_category pc ON pt.id_category = pc.id_category
                    WHERE pt.id_type IN (
                        SELECT id_type FROM aircraft_instance WHERE id_shop = %s
                        UNION
                        SELECT id_type FROM rocket_instance WHERE id_shop = %s
                        UNION
                        SELECT id_type FROM glider_instance WHERE id_shop = %s
                        UNION
                        SELECT id_type FROM helicopter_instance WHERE id_shop = %s
                        UNION
                        SELECT id_type FROM hangglider_instance WHERE id_shop = %s
                        UNION
                        SELECT id_type FROM other_instance WHERE id_shop = %s
                    )
                    AND (pt.id_category = %s OR %s IS NULL)
                    ORDER BY pt.name
                    """,
                    (shop_id, shop_id, shop_id, shop_id, shop_id, shop_id,
                     category_id, category_id),
                )
                return [(row[0],) for row in cur.fetchall()]
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
    ) -> Tuple[int, List[Tuple]]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT serial_number, product_type_name, shop_name,
                           category_name, completion_date
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
                rows = cur.fetchall()
                return len(rows), rows
        except psycopg2.Error as e:
            print(f"Ошибка в query2_completed_products: {e}")
            return 0, []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query3_workers(
        self, shop_id: Optional[int] = None, section_id: Optional[int] = None
    ) -> List[Tuple]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        last_name || ' ' || first_name || ' ' || COALESCE(middle_name, '') AS fio,
                        profession,
                        rank,
                        brigade_name,
                        section_name,
                        shop_name
                    FROM view_workers
                    WHERE (id_shop = %s OR %s IS NULL)
                      AND (id_section = %s OR %s IS NULL)
                    ORDER BY last_name, first_name
                    """,
                    (shop_id, shop_id, section_id, section_id),
                )
                return cur.fetchall()
        except psycopg2.Error as e:
            print(f"Ошибка в query3_workers: {e}")
            return []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query3_engineers(
        self, category: Optional[str] = None
    ) -> List[Tuple]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        last_name || ' ' || first_name || ' ' || COALESCE(middle_name, '') AS fio,
                        category,
                        position
                    FROM view_engineers
                    WHERE (category = %s OR %s IS NULL)
                    ORDER BY last_name, first_name
                    """,
                    (category, category),
                )
                return cur.fetchall()
        except psycopg2.Error as e:
            print(f"Ошибка в query3_engineers: {e}")
            return []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query4_sections_with_managers(
        self, shop_id: Optional[int] = None
    ) -> List[Tuple]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        section_name,
                        shop_name,
                        manager_last_name || ' ' || manager_first_name || ' ' || COALESCE(manager_middle_name, '') AS manager_fio,
                        manager_position
                    FROM view_sections_with_managers
                    WHERE (id_shop = %s OR %s IS NULL)
                    ORDER BY id_section
                    """,
                    (shop_id, shop_id),
                )
                return cur.fetchall()
        except psycopg2.Error as e:
            print(f"Ошибка в query4_sections_with_managers: {e}")
            return []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query5_work_steps(self, serial_number: int) -> List[Tuple]:
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
                return cur.fetchall()
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
    ) -> List[Tuple]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        brigade_name,
                        section_name,
                        shop_name,
                        last_name || ' ' || first_name || ' ' || COALESCE(middle_name, '') AS fio,
                        profession,
                        rank,
                        CASE WHEN is_foreman THEN 'Да' ELSE 'Нет' END AS is_foreman_str
                    FROM view_brigade_members
                    WHERE (id_brigade = %s OR %s IS NULL)
                      AND (id_section = %s OR %s IS NULL)
                      AND (id_shop = %s OR %s IS NULL)
                    ORDER BY brigade_name, last_name
                    """,
                    (brigade_id, brigade_id, section_id, section_id,
                     shop_id, shop_id),
                )
                return cur.fetchall()
        except psycopg2.Error as e:
            print(f"Ошибка в query6_brigade_members: {e}")
            return []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query7_masters(
        self, shop_id: Optional[int] = None, section_id: Optional[int] = None
    ) -> List[Tuple]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        last_name || ' ' || first_name || ' ' || COALESCE(middle_name, '') AS fio,
                        category,
                        position
                    FROM view_masters
                    ORDER BY last_name, first_name
                    """
                )
                return cur.fetchall()
        except psycopg2.Error as e:
            print(f"Ошибка в query7_masters: {e}")
            return []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query8_products_in_assembly(
        self, shop_id: Optional[int] = None, category_id: Optional[int] = None
    ) -> List[Tuple]:
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
                return cur.fetchall()
        except psycopg2.Error as e:
            print(f"Ошибка в query8_products_in_assembly: {e}")
            return []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query9_brigades_for_product(self, serial_number: int) -> List[Tuple]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT DISTINCT
                        b.name AS brigade_name,
                        sec.name AS section_name,
                        e.last_name || ' ' || e.first_name || ' ' || COALESCE(e.middle_name, '') AS fio,
                        w.profession
                    FROM product_instance pi
                    JOIN work_execution we ON we.serial_number = pi.serial_number
                    JOIN work_step ws ON we.id_step = ws.id_step
                    JOIN section_work_list swl ON ws.id_work = swl.id_work
                    JOIN section sec ON swl.id_section = sec.id_section
                    JOIN brigade b ON b.id_section = sec.id_section
                    JOIN worker w ON w.id_brigade = b.id_brigade
                    JOIN employee e ON w.id_employee = e.id_employee
                    WHERE pi.serial_number = %s
                    ORDER BY b.name, e.last_name
                    """,
                    (serial_number,),
                )
                return cur.fetchall()
        except psycopg2.Error as e:
            print(f"Ошибка в query9_brigades_for_product: {e}")
            return []
        finally:
            if conn is not None:
                self.db.return_connection(conn)

    def query10_labs_for_product(self, serial_number: int) -> List[Tuple]:
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
                return cur.fetchall()
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
    ) -> List[Tuple]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        serial_number,
                        product_type_name,
                        category_name,
                        lab_name,
                        test_date,
                        test_result
                    FROM view_tested_products
                    WHERE (id_lab = %s OR %s IS NULL)
                      AND (id_category = %s OR %s IS NULL)
                      AND (test_date >= %s OR %s IS NULL)
                      AND (test_date <= %s OR %s IS NULL)
                    ORDER BY test_date
                    """,
                    (lab_id, lab_id, category_id, category_id,
                     start_date, start_date, end_date, end_date),
                )
                return cur.fetchall()
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
    ) -> List[Tuple]:
        conn = None
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT DISTINCT
                        e.last_name || ' ' || e.first_name || ' ' || COALESCE(e.middle_name, '') AS fio,
                        t.specialization
                    FROM employee e
                    JOIN tester t ON e.id_employee = t.id_employee
                    JOIN tester_equipment teq ON t.id_employee = teq.id_tester
                    JOIN equipment eq ON teq.id_equipment = eq.id_equipment
                    JOIN test_work_list twl ON eq.id_equipment = twl.id_equipment
                    JOIN test_step ts ON twl.id_test_work = ts.id_test_work
                    JOIN test_execution te ON ts.id_step = te.id_test_step
                    JOIN product_instance pi ON te.serial_number = pi.serial_number
                    JOIN product_type pt ON pi.id_type = pt.id_type
                    JOIN product_category pc ON pt.id_category = pc.id_category
                    WHERE (te.serial_number = %s OR %s IS NULL)
                      AND (pt.id_category = %s OR %s IS NULL)
                      AND (eq.id_lab = %s OR %s IS NULL)
                      AND (te.end_date >= %s OR %s IS NULL)
                      AND (te.end_date <= %s OR %s IS NULL)
                    ORDER BY fio
                    """,
                    (serial_number, serial_number, category_id, category_id,
                     lab_id, lab_id, start_date, start_date,
                     end_date, end_date),
                )
                return cur.fetchall()
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
    ) -> List[Tuple]:
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
                return cur.fetchall()
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
    ) -> Tuple[int, List[Tuple]]:
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
                    SELECT 
                        shop_name,
                        section_name,
                        category_name,
                        product_count
                    FROM view_products_in_assembly_summary
                    WHERE (id_shop = %s OR %s IS NULL)
                      AND (id_section = %s OR %s IS NULL)
                    ORDER BY shop_name, section_name, category_name
                    """,
                    (shop_id, shop_id, section_id, section_id),
                )
                rows = cur.fetchall()
                return total, rows
        except psycopg2.Error as e:
            print(f"Ошибка в query14_assembly_summary: {e}")
            return 0, []
        finally:
            if conn is not None:
                self.db.return_connection(conn)