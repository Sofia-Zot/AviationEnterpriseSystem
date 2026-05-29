

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
)

from dao.query_dao import QueryDAO
from gui.queries.base_query_window import BaseQueryWindow


class Query13Window(BaseQueryWindow):


    def __init__(self, query_dao: QueryDAO, parent=None):
        super().__init__(query_dao, parent)
        self.setWindowTitle("Запрос 13 – Оборудование")
        self._load_filters()

    def _get_title(self) -> str:
        return "Запрос 13: Оборудование для испытаний"

    def _create_params_widget(self) -> QWidget:
        """Создаёт виджет с параметрами."""
        widget = QWidget()
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Изделие (серийный №):"))
        self.edit_serial = QLineEdit()
        self.edit_serial.setPlaceholderText("Не заполнено")
        layout.addWidget(self.edit_serial)

        layout.addWidget(QLabel("Лаборатория:"))
        self.cb_lab = QComboBox()
        self.cb_lab.addItem("Все лаборатории", None)
        layout.addWidget(self.cb_lab)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _load_filters(self):
        """Загружает список лабораторий."""
        try:
            from db.connection import DatabaseConnection
            db = DatabaseConnection()
            conn = db.get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT id_lab, name FROM laboratory ORDER BY name")
                    for row in cur.fetchall():
                        self.cb_lab.addItem(row[1], row[0])
            finally:
                db.return_connection(conn)
        except Exception as e:
            self.status_bar.showMessage(f"Ошибка загрузки фильтров: {e}")

    def _execute_query(self):
        """Выполняет запрос 13."""
        serial_text = self.edit_serial.text().strip()
        serial_number = int(serial_text) if serial_text else None

        lab_id = self.cb_lab.currentData()
        if lab_id == "":
            lab_id = None

        data = self.query_dao.query13_equipment_for_tests(
            serial_number=serial_number,
            lab_id=lab_id
        )

        columns = ["Оборудование", "Модель"]
        self.display_results(data, columns=columns)
