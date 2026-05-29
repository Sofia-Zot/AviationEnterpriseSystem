from typing import Optional


class Brigade:


    def __init__(
        self,
        id_brigade: int = 0,
        name: str = "",
        id_section: int = 0,
        id_foreman: Optional[int] = None,
        section_name: Optional[str] = None,
        shop_name: Optional[str] = None,
        foreman_name: Optional[str] = None,
    ):
        self.id_brigade = id_brigade
        self.name = name
        self.id_section = id_section
        self.id_foreman = id_foreman
        self.section_name = section_name
        self.shop_name = shop_name
        self.foreman_name = foreman_name

    def __repr__(self) -> str:
        return f"Brigade(id={self.id_brigade}, name={self.name})"
