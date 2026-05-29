
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
)

from dao.query_dao import QueryDAO
from gui.queries.base_query_window import BaseQueryWindow


class Query6Window(BaseQueryWindow):
    def __init__(self, query_dao: QueryDAO, parent=None):
        super().__init__(query_dao, parent)
        self.setWindowTitle("Запрос 6 – Состав бригад")
        self._load_filters()

    def _get_title(self) -> str:
        return "Запрос 6: Состав бригад"

    def _create_params_widget(self) -> QWidget:
        """Создаёт виджет с параметрами."""
        widget = QWidget()
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Цех:"))
        self.cb_shop = QComboBox()
        self.cb_shop.addItem("Все цеха", None)
        layout.addWidget(self.cb_shop)

        layout.addWidget(QLabel("Участок:"))
        self.cb_section = QComboBox()
        self.cb_section.addItem("Все участки", None)
        layout.addWidget(self.cb_section)

        layout.addWidget(QLabel("Бригада:"))
        self.cb_brigade = QComboBox()
        self.cb_brigade.addItem("Все бригады", None)
        layout.addWidget(self.cb_brigade)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _load_filters(self):
        """Загружает списки цехов, участков и бригад."""
        try:
            from db.connection import DatabaseConnection
            db = DatabaseConnection()
            conn = db.get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT id_shop, name FROM shop ORDER BY name")
                    for row in cur.fetchall():
                        self.cb_shop.addItem(row[1], row[0])

                    cur.execute("SELECT id_section, name FROM section ORDER BY id_shop, name")
                    for row in cur.fetchall():
                        self.cb_section.addItem(row[1], row[0])

                    cur.execute("SELECT id_brigade, name FROM brigade ORDER BY name")
                    for row in cur.fetchall():
                        self.cb_brigade.addItem(row[1], row[0])
            finally:
                db.return_connection(conn)
        except Exception as e:
            self.status_bar.showMessage(f"Ошибка загрузки фильтров: {e}")

    def _execute_query(self):
        """Выполняет запрос 6."""
        shop_id = self.cb_shop.currentData()
        section_id = self.cb_section.currentData()
        brigade_id = self.cb_brigade.currentData()

        if shop_id == "":
            shop_id = None
        if section_id == "":
            section_id = None
        if brigade_id == "":
            brigade_id = None

        data = self.query_dao.query6_brigade_members(
            brigade_id=brigade_id,
            section_id=section_id,
            shop_id=shop_id
        )

        columns = ["Бригада", "Участок", "Цех", "ФИО", "Профессия", "Разряд", "Бригадир"]
        self.display_results(data, columns=columns)
