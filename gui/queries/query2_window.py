

from datetime import date
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QDateEdit,
)
from PyQt5.QtCore import QDate

from dao.query_dao import QueryDAO
from gui.queries.base_query_window import BaseQueryWindow


class Query2Window(BaseQueryWindow):


    def __init__(self, query_dao: QueryDAO, parent=None):
        super().__init__(query_dao, parent)
        self.setWindowTitle("Запрос 2 – Завершённые изделия")
        self._load_filters()

    def _get_title(self) -> str:
        return "Запрос 2: Завершённые изделия за период"

    def _create_params_widget(self) -> QWidget:
        """Создаёт виджет с параметрами."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Выбор цеха и категории
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Цех:"))
        self.cb_shop = QComboBox()
        self.cb_shop.addItem("Все цеха", None)
        row1.addWidget(self.cb_shop)

        row1.addWidget(QLabel("Категория:"))
        self.cb_category = QComboBox()
        self.cb_category.addItem("Все категории", None)
        row1.addWidget(self.cb_category)
        row1.addStretch()
        layout.addLayout(row1)

        # Выбор периода
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Период:"))
        row2.addWidget(QLabel("С:"))
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate(2024, 1, 1))
        row2.addWidget(self.date_start)

        row2.addWidget(QLabel("По:"))
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QDate.currentDate())
        row2.addWidget(self.date_end)
        row2.addStretch()
        layout.addLayout(row2)

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
        """Выполняет запрос 2."""
        shop_id = self.cb_shop.currentData()
        category_id = self.cb_category.currentData()

        start_date = self.date_start.date().toPyDate()
        end_date = self.date_end.date().toPyDate()

        # Преобразуем None для DAO
        if shop_id == "":
            shop_id = None
        if category_id == "":
            category_id = None

        count, data = self.query_dao.query2_completed_products(
            shop_id=shop_id,
            category_id=category_id,
            start_date=start_date,
            end_date=end_date
        )

        columns = ["Серийный №", "Вид изделия", "Цех", "Категория", "Дата завершения"]
        self.display_results(data, columns=columns)
        self.status_bar.showMessage(f"Найдено изделий: {count}")
