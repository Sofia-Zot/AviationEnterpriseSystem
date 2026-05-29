class Engineer:
    def __init__(
        self,
        id_employee: int = 0,
        category: str = "",
        position: str = "",
    ):
        self.id_employee = id_employee
        self.category = category
        self.position = position

    def __repr__(self) -> str:
        return f"Engineer(id_employee={self.id_employee}, position={self.position})"
