class Section:
    def __init__(self, id_section: int = 0, name: str = "", id_shop: int = 0):
        self.id_section = id_section
        self.name = name
        self.id_shop = id_shop

    def __repr__(self) -> str:
        return f"Section(id={self.id_section}, name={self.name}, shop={self.id_shop})"
