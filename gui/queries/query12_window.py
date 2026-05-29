

from datetime import date
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QDateEdit,
    QLineEdit,
)
from PyQt5.QtCore import QDate

from dao.query_dao import QueryDAO
from gui.queries.base_query_window import BaseQueryWindow


class Query12Window(BaseQueryWindow):


    def __init__(self, query_dao: QueryDAO, parent=None):
        super().__init__(query_dao, parent)
        self.setWindowTitle("Запрос 12 – Испытатели")
        self._load_filters()

    def _get_title(self) -> str:
        return "Запрос 12: Испытатели"

    def _create_params_widget(self) -> QWidget:
        """Создаёт виджет с параметрами."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Изделие, категория, лаборатория
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Изделие (серийный №):"))
        self.edit_serial = QLineEdit()
        self.edit_serial.setPlaceholderText("Не заполнено")
        row1.addWidget(self.edit_serial)

        row1.addWidget(QLabel("Категория:"))
        self.cb_category = QComboBox()
        self.cb_category.addItem("Все категории", None)
        row1.addWidget(self.cb_category)

        row1.addWidget(QLabel("Лаборатория:"))
        self.cb_lab = QComboBox()
        self.cb_lab.addItem("Все лаборатории", None)
        row1.addWidget(self.cb_lab)
        row1.addStretch()
        layout.addLayout(row1)

        # Период
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
        """Загружает списки категорий и лабораторий."""
        try:
            from db.connection import DatabaseConnection
            db = DatabaseConnection()
            conn = db.get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT id_category, name FROM product_category ORDER BY name")
                    for row in cur.fetchall():
                        self.cb_category.addItem(row[1], row[0])

                    cur.execute("SELECT id_lab, name FROM laboratory ORDER BY name")
                    for row in cur.fetchall():
                        self.cb_lab.addItem(row[1], row[0])
            finally:
                db.return_connection(conn)
        except Exception as e:
            self.status_bar.showMessage(f"Ошибка загрузки фильтров: {e}")

    def _execute_query(self):
        """Выполняет запрос 12."""
        serial_text = self.edit_serial.text().strip()
        serial_number = int(serial_text) if serial_text else None

        category_id = self.cb_category.currentData()
        lab_id = self.cb_lab.currentData()
        start_date = self.date_start.date().toPyDate()
        end_date = self.date_end.date().toPyDate()

        if category_id == "":
            category_id = None
        if lab_id == "":
            lab_id = None

        data = self.query_dao.query12_testers(
            serial_number=serial_number,
            category_id=category_id,
            lab_id=lab_id,
            start_date=start_date,
            end_date=end_date
        )

        columns = ["ФИО", "Специализация"]
        self.display_results(data, columns=columns)
