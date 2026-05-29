class ProductType:
    def __init__(
        self,
        id_type: int = 0,
        name: str = "",
        id_category: int = 0,
        category_name: str = None,
    ):
        self.id_type = id_type
        self.name = name
        self.id_category = id_category
        self.category_name = category_name

    def __repr__(self) -> str:
        return f"ProductType(id={self.id_type}, name={self.name})"
