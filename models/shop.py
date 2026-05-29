class Shop:
    def __init__(self, id_shop: int = 0, name: str = ""):
        self.id_shop = id_shop
        self.name = name

    def __repr__(self) -> str:
        return f"Shop(id={self.id_shop}, name={self.name})"
