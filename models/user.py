from typing import Optional


class User:
    def __init__(
        self,
        login: str = "",
        password_hash: str = "",
        role: str = "",
        id_employee: Optional[int] = None,
    ):
        self.login = login
        self.password_hash = password_hash
        self.role = role
        self.id_employee = id_employee

    def __repr__(self) -> str:
        return f"User(login={self.login}, role={self.role})"

    def __str__(self) -> str:
        return f"User: {self.login} ({self.role})"

