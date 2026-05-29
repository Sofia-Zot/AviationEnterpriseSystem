

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
)

from dao.query_dao import QueryDAO
from gui.queries.base_query_window import BaseQueryWindow


class Query8Window(BaseQueryWindow):


    def __init__(self, query_dao: QueryDAO, parent=None):
        super().__init__(query_dao, parent)
        self.setWindowTitle("Запрос 8 – Изделия в сборке")
        self._load_filters()

    def _get_title(self) -> str:
        return "Запрос 8: Изделия в сборке"

    def _create_params_widget(self) -> QWidget:
        """Создаёт виджет с параметрами."""
        widget = QWidget()
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Цех:"))
        self.cb_shop = QComboBox()
        self.cb_shop.addItem("Все цеха", None)
        layout.addWidget(self.cb_shop)

        layout.addWidget(QLabel("Категория:"))
        self.cb_category = QComboBox()
        self.cb_category.addItem("Все категории", None)
        layout.addWidget(self.cb_category)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _load_filters(self):
        """Загружает списки цехов и категорий."""
        try:
            from db.connection import DatabaseConnection
            db = DatabaseConnection()
            conn = db.get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT id_shop, name FROM shop ORDER BY name")
                    for row in cur.fetchall():
                        self.cb_shop.addItem(row[1], row[0])

                    cur.execute("SELECT id_category, name FROM product_category ORDER BY name")
                    for row in cur.fetchall():
                        self.cb_category.addItem(row[1], row[0])
            finally:
                db.return_connection(conn)
        except Exception as e:
            self.status_bar.showMessage(f"Ошибка загрузки фильтров: {e}")

    def _execute_query(self):
        """Выполняет запрос 8."""
        shop_id = self.cb_shop.currentData()
        category_id = self.cb_category.currentData()

        if shop_id == "":
            shop_id = None
        if category_id == "":
            category_id = None

        data = self.query_dao.query8_products_in_assembly(
            shop_id=shop_id,
            category_id=category_id
        )

        columns = ["Серийный №", "Вид изделия", "Цех"]
        self.display_results(data, columns=columns)
