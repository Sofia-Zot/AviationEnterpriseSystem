from typing import List, Optional
import psycopg2
from db.connection import DatabaseConnection
from models.employee import Employee
from dao.base_dao import BaseDAO


class EmployeeDAO(BaseDAO[Employee]):
    def get_all(self) -> List[Employee]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id_employee, last_name, first_name, middle_name,
                           birth_date, education, hire_date, prior_exp,
                           address, phone, salary, other_info
                    FROM employee
                    ORDER BY id_employee
                    """
                )
                rows = cur.fetchall()
                result = []
                for row in rows:
                    result.append(Employee(
                        id_employee=row[0],
                        last_name=row[1],
                        first_name=row[2],
                        middle_name=row[3],
                        birth_date=row[4],
                        education=row[5],
                        hire_date=row[6],
                        prior_exp=row[7],
                        address=row[8],
                        phone=row[9],
                        salary=row[10],
                        other_info=row[11],
                    ))
                return result
        except psycopg2.Error as e:
            print(f"Ошибка при получении списка сотрудников: {e}")
            return []
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def get_by_id(self, id: int) -> Optional[Employee]:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id_employee, last_name, first_name, middle_name,
                           birth_date, education, hire_date, prior_exp,
                           address, phone, salary, other_info
                    FROM employee
                    WHERE id_employee = %s
                    """,
                    (id,),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                return Employee(
                    id_employee=row[0],
                    last_name=row[1],
                    first_name=row[2],
                    middle_name=row[3],
                    birth_date=row[4],
                    education=row[5],
                    hire_date=row[6],
                    prior_exp=row[7],
                    address=row[8],
                    phone=row[9],
                    salary=row[10],
                    other_info=row[11],
                )
        except psycopg2.Error as e:
            print(f"Ошибка при получении сотрудника по ID: {e}")
            return None
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def insert(self, entity: Employee) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO employee (
                        last_name, first_name, middle_name, birth_date,
                        education, hire_date, prior_exp, address, phone, salary, other_info
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_employee
                    """,
                    (
                        entity.last_name,
                        entity.first_name,
                        entity.middle_name,
                        entity.birth_date,
                        entity.education,
                        entity.hire_date,
                        entity.prior_exp,
                        entity.address,
                        entity.phone,
                        entity.salary,
                        entity.other_info,
                    ),
                )
                row = cur.fetchone()
                if row:
                    entity.id_employee = row[0]
                conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Ошибка при добавлении сотрудника: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)

    def update(self, entity: Employee) -> bool:
        conn = None
        try:
            conn = DatabaseConnection().get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE employee
                    SET last_name = %s, first_name = %s, middle_name = %s,
                        birth_date = %s, education = %s, hire_date = %s,
                        prior_exp = %s, address = %s, phone = %s, salary = %s,
                        other_info = %s
                    WHERE id_employee = %s
                    """,
                    (
                        entity.last_name,
                        entity.first_name,
                        entity.middle_name,
                        entity.birth_date,
                        entity.education,
                        entity.hire_date,
                        entity.prior_exp,
                        entity.address,
                        entity.phone,
                        entity.salary,
                        entity.other_info,
                        entity.id_employee,
                    ),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при обновлении сотрудника: {e}")
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
                # Сначала удаляем записи из таблиц подтипов (worker, engineer, tester)
                cur.execute("DELETE FROM worker WHERE id_employee = %s", (id,))
                cur.execute("DELETE FROM engineer WHERE id_employee = %s", (id,))
                cur.execute("DELETE FROM tester WHERE id_employee = %s", (id,))

                # Затем удаляем основную запись из employee
                cur.execute(
                    "DELETE FROM employee WHERE id_employee = %s",
                    (id,),
                )
                conn.commit()
                return cur.rowcount == 1
        except psycopg2.Error as e:
            print(f"Ошибка при удалении сотрудника: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn is not None:
                DatabaseConnection().return_connection(conn)
