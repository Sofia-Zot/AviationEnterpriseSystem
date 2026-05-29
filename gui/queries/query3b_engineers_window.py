

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
)

from dao.query_dao import QueryDAO
from gui.queries.base_query_window import BaseQueryWindow


class Query3bEngineersWindow(BaseQueryWindow):


    def __init__(self, query_dao: QueryDAO, parent=None):
        super().__init__(query_dao, parent)
        self.setWindowTitle("Запрос 3b – ИТР")
        self._load_filters()

    def _get_title(self) -> str:
        return "Запрос 3b: Кадровый состав (ИТР)"

    def _create_params_widget(self) -> QWidget:
        """Создаёт виджет с параметрами."""
        widget = QWidget()
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Категория:"))
        self.cb_category = QComboBox()
        self.cb_category.addItem("Все категории", None)
        self.cb_category.addItem("Engineer")
        self.cb_category.addItem("Technologist")
        self.cb_category.addItem("Technician")
        layout.addWidget(self.cb_category)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _execute_query(self):
        """Выполняет запрос 3b."""
        category = self.cb_category.currentText()
        if category == "Все категории":
            category = None

        data = self.query_dao.query3_engineers(category=category)

        columns = ["ФИО", "Категория", "Должность"]
        self.display_results(data, columns=columns)
