

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
)

from dao.query_dao import QueryDAO
from gui.queries.base_query_window import BaseQueryWindow


class Query10Window(BaseQueryWindow):

    def __init__(self, query_dao: QueryDAO, parent=None):
        super().__init__(query_dao, parent)
        self.setWindowTitle("Запрос 10 – Лаборатории")

    def _get_title(self) -> str:
        return "Запрос 10: Лаборатории для изделия"

    def _create_params_widget(self) -> QWidget:
        """Создаёт виджет с параметрами."""
        widget = QWidget()
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Серийный номер изделия:"))
        self.edit_serial = QLineEdit()
        self.edit_serial.setPlaceholderText("Введите номер")
        layout.addWidget(self.edit_serial)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _execute_query(self):
        """Выполняет запрос 10."""
        serial_text = self.edit_serial.text().strip()
        if not serial_text:
            self.status_bar.showMessage("Введите серийный номер")
            return

        try:
            serial_number = int(serial_text)
        except ValueError:
            self.status_bar.showMessage("Серийный номер должен быть числом")
            return

        data = self.query_dao.query10_labs_for_product(serial_number=serial_number)

        columns = ["Лаборатория", "Тип"]
        self.display_results(data, columns=columns)
