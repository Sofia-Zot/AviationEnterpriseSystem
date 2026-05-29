from datetime import date
from typing import List

from models.employee import Employee


def validate_rank(rank: int) -> bool:
    return 1 <= rank <= 6


def validate_date_not_future(value: date) -> bool:
    return value <= date.today()


def validate_status(status: str) -> bool:
    return status in ("in_assembly", "under_test", "ready")


def validate_required_string(value: str, max_len: int = 100) -> bool:
    return isinstance(value, str) and 0 < len(value.strip()) <= max_len


def validate_employee_data(employee: Employee) -> List[str]:
    errors = []

    if not validate_required_string(employee.last_name):
        errors.append("Фамилия обязательна и не должна превышать 100 символов.")

    if not validate_required_string(employee.first_name):
        errors.append("Имя обязательно и не должно превышать 100 символов.")

    if employee.middle_name is not None and not validate_required_string(
        employee.middle_name
    ):
        errors.append("Отчество не должно быть пустым, если указано.")

    if employee.birth_date is not None and not validate_date_not_future(
        employee.birth_date
    ):
        errors.append("Дата рождения не может быть в будущем.")

    if employee.hire_date is not None and not validate_date_not_future(
        employee.hire_date
    ):
        errors.append("Дата приёма не может быть в будущем.")

    if employee.prior_exp is not None and employee.prior_exp < 0:
        errors.append("Предыдущий стаж не может быть отрицательным.")

    if employee.salary is not None and employee.salary < 0:
        errors.append("Зарплата не может быть отрицательной.")

    return errors
