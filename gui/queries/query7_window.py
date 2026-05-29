

from PyQt5.QtWidgets import QWidget

from dao.query_dao import QueryDAO
from gui.queries.base_query_window import BaseQueryWindow


class Query7Window(BaseQueryWindow):


    def __init__(self, query_dao: QueryDAO, parent=None):
        super().__init__(query_dao, parent)
        self.setWindowTitle("Запрос 7 – Мастера")

    def _get_title(self) -> str:
        return "Запрос 7: Список мастеров"

    def _create_params_widget(self) -> QWidget:
        """Параметры отсутствуют (фильтрация по цеху/участку невозможна)."""
        return None

    def _execute_query(self):
        """Выполняет запрос 7."""
        data = self.query_dao.query7_masters()

        columns = ["ФИО", "Категория", "Должность"]
        self.display_results(data, columns=columns)
