

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
)

from dao.query_dao import QueryDAO
from gui.queries.base_query_window import BaseQueryWindow


class Query4Window(BaseQueryWindow):

    def __init__(self, query_dao: QueryDAO, parent=None):
        super().__init__(query_dao, parent)
        self.setWindowTitle("Запрос 4 – Участки и начальники")
        self._load_filters()

    def _get_title(self) -> str:
        return "Запрос 4: Участки и их начальники"

    def _create_params_widget(self) -> QWidget:
        """Создаёт виджет с параметрами."""
        widget = QWidget()
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Цех:"))
        self.cb_shop = QComboBox()
        self.cb_shop.addItem("Все цеха", None)
        layout.addWidget(self.cb_shop)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _load_filters(self):
        """Загружает списки цехов."""
        try:
            from db.connection import DatabaseConnection
            db = DatabaseConnection()
            conn = db.get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT id_shop, name FROM shop ORDER BY name")
                    for row in cur.fetchall():
                        self.cb_shop.addItem(row[1], row[0])
            finally:
                db.return_connection(conn)
        except Exception as e:
            self.status_bar.showMessage(f"Ошибка загрузки фильтров: {e}")

    def _execute_query(self):
        """Выполняет запрос 4."""
        shop_id = self.cb_shop.currentData()
        if shop_id == "":
            shop_id = None

        data = self.query_dao.query4_sections_with_managers(shop_id=shop_id)

        columns = ["Участок", "Цех", "Начальник (ФИО)", "Должность"]
        self.display_results(data, columns=columns)
