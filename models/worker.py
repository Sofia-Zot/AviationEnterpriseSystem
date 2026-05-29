class Worker:

    def __init__(
        self,
        id_employee: int = 0,
        profession: str = "",
        rank: int = 1,
        is_foreman: bool = False,
        id_brigade: int = 0,
    ):
        self.id_employee = id_employee
        self.profession = profession
        self.rank = rank
        self.is_foreman = is_foreman
        self.id_brigade = id_brigade

    def __repr__(self) -> str:
        return (
            f"Worker(id_employee={self.id_employee}, "
            f"profession={self.profession}, rank={self.rank})"
        )
