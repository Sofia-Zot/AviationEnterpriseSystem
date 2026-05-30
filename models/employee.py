from datetime import date
from typing import Optional


class Employee:


    def __init__(
        self,
        id_employee: int = 0,
        last_name: str = "",
        first_name: str = "",
        middle_name: Optional[str] = None,
        birth_date: Optional[date] = None,
        education: Optional[str] = None,
        hire_date: Optional[date] = None,
        prior_exp: Optional[int] = None,
        address: Optional[str] = None,
        phone: Optional[str] = None,
        salary: Optional[float] = None,
        other_info: Optional[str] = None,
    ):
        self.id_employee = id_employee
        self.last_name = last_name
        self.first_name = first_name
        self.middle_name = middle_name
        self.birth_date = birth_date
        self.education = education
        self.hire_date = hire_date
        self.prior_exp = prior_exp
        self.address = address
        self.phone = phone
        self.salary = salary
        self.other_info = other_info

    def __repr__(self) -> str:
        return f"Employee(id={self.id_employee}, {self.last_name} {self.first_name})"
