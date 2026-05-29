from typing import Optional


class ProductInstance:
    def __init__(
        self,
        serial_number: int = 0,
        status: str = "in_assembly",
        id_shop: int = 0,
        id_type: int = 0,
        weight: Optional[float] = None,
        material: Optional[str] = None,
        batch: Optional[str] = None,
        product_type_name: Optional[str] = None,
        product_category_name: Optional[str] = None,
        shop_name: Optional[str] = None,
    ):
        self.serial_number = serial_number
        self.status = status
        self.id_shop = id_shop
        self.id_type = id_type
        self.weight = weight
        self.material = material
        self.batch = batch
        self.product_type_name = product_type_name
        self.product_category_name = product_category_name
        self.shop_name = shop_name

    def __repr__(self) -> str:
        return f"ProductInstance(sn={self.serial_number}, status={self.status})"
