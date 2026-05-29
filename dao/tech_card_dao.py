
from typing import List, Optional
import psycopg2
from db.connection import DatabaseConnection
from models.tech_card import TechCard
from dao.base_dao import BaseDAO


class TechCardDAO(BaseDAO[TechCard]):
    def get_all(self) -> List[TechCard]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id_card, id_type
                    FROM tech_card
                    ORDER BY id_card
                    """
                )
                rows = cur.fetchall()
                return [
                    TechCard(
                        id_card=row[0],
                        id_type=row[1],
                    )
                    for row in rows
                ]
        except psycopg2.Error as e:
            print(f"Ошибка при получении списка техкарт: {e}")
            return []
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def get_all_with_relations(self) -> List[TechCard]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        tc.id_card,
                        tc.id_type,
                        pt.name AS product_type_name
                    FROM tech_card tc
                    JOIN product_type pt ON tc.id_type = pt.id_type
                    ORDER BY tc.id_card
                """)
                rows = cur.fetchall()
                return [
                    TechCard(
                        id_card=row[0],
                        id_type=row[1],
                        product_type_name=row[2],
                    )
                    for row in rows
                ]
        except psycopg2.Error as e:
            print(f"Ошибка при получении списка техкарт: {e}")
            return []
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def get_by_id(self, id: int) -> Optional[TechCard]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id_card, id_type
                    FROM tech_card
                    WHERE id_card = %s
                    """,
                    (id,),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                return TechCard(
                    id_card=row[0],
                    id_type=row[1],
                )
        except psycopg2.Error as e:
            print(f"Ошибка при получении техкарты по ID: {e}")
            return None
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def insert(self, entity: TechCard) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO tech_card (id_type)
                    VALUES (%s)
                    RETURNING id_card
                    """,
                    (entity.id_type,),
                )
                row = cur.fetchone()
                if row:
                    entity.id_card = row[0]
                conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Ошибка при добавлении техкарты: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def update(self, entity: TechCard) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE tech_card
                    SET id_type = %s
                    WHERE id_card = %s
                    """,
                    (
                        entity.id_type,
                        entity.id_card,
                    ),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при обновлении техкарты: {e}")
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
                # Сначала удаляем все этапы (work_step), связанные с картой
                cur.execute(
                    "DELETE FROM work_step WHERE id_card = %s",
                    (id,),
                )
                # Затем удаляем саму карту
                cur.execute(
                    "DELETE FROM tech_card WHERE id_card = %s",
                    (id,),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при удалении техкарты: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def get_steps(self, card_id: int) -> List[dict]:
        """Получает этапы техкарты."""
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT ws.id_step, ws.id_work, swl.work_name, s.name as section_name
                    FROM work_step ws
                    JOIN section_work_list swl ON ws.id_work = swl.id_work
                    JOIN section s ON swl.id_section = s.id_section
                    WHERE ws.id_card = %s
                    ORDER BY ws.step_number
                    """,
                    (card_id,),
                )
                rows = cur.fetchall()
                result = []
                for row in rows:
                    result.append({
                        'id_step': row[0],
                        'id_work': row[1],
                        'work_name': row[2],
                        'section_name': row[3],
                    })
                return result
        except psycopg2.Error as e:
            print(f"Ошибка при получении этапов техкарты: {e}")
            return []
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def add_step(self, card_id: int, work_id: int, step_number: int = None) -> bool:
        """Добавляет этап к техкарте."""
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                # Если номер шага не указан, берём следующий
                if step_number is None:
                    cur.execute(
                        "SELECT COALESCE(MAX(step_number), 0) + 1 FROM work_step WHERE id_card = %s",
                        (card_id,),
                    )
                    step_number = cur.fetchone()[0]

                cur.execute(
                    """
                    INSERT INTO work_step (id_card, id_work, step_number)
                    VALUES (%s, %s, %s)
                    RETURNING id_step
                    """,
                    (card_id, work_id, step_number),
                )
                conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Ошибка при добавлении этапа: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def delete_step(self, step_id: int) -> bool:
        """Удаляет конкретный этап."""
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM work_step WHERE id_step = %s",
                    (step_id,),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при удалении этапа: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def delete_steps(self, card_id: int) -> bool:
        """Удаляет все этапы техкарты."""
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM work_step WHERE id_card = %s",
                    (card_id,),
                )
                conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Ошибка при удалении этапов: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)
