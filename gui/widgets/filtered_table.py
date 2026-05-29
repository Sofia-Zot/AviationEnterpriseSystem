

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
)
from PyQt5.QtCore import Qt


class FilteredTable(QWidget):


    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск по таблице...")
        layout.addWidget(self.search_edit)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.search_edit.textChanged.connect(self._apply_filter)

    # ---------- удобные методы для работы с данными ----------

    def set_headers(self, headers):
        """Устанавливает заголовки столбцов."""
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

    def add_row(self, values, row_data=None):
        """Добавляет строку в конец таблицы."""
        row = self.table.rowCount()
        self.table.insertRow(row)
        for col, val in enumerate(values):
            item = QTableWidgetItem(str(val) if val is not None else "")
            item.setData(Qt.UserRole, row_data)
            self.table.setItem(row, col, item)

    def clear(self):
        """Очищает все строки."""
        self.table.setRowCount(0)

    def _apply_filter(self, text):
        """Скрывает строки, не содержащие подстроку поиска."""
        text = text.lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    # ---------- прокси к внутреннему QTableWidget ----------

    def horizontalHeader(self):
        return self.table.horizontalHeader()

    def setSelectionBehavior(self, behavior):
        self.table.setSelectionBehavior(behavior)

    def setEditTriggers(self, triggers):
        self.table.setEditTriggers(triggers)

    def setSelectionMode(self, mode):
        self.table.setSelectionMode(mode)

    def setCellWidget(self, row, column, widget):
        self.table.setCellWidget(row, column, widget)

    def selectedItems(self):
        return self.table.selectedItems()

    def currentRow(self):
        return self.table.currentRow()

    def item(self, row, column):
        return self.table.item(row, column)

    def rowCount(self):
        return self.table.rowCount()

    def setRowHidden(self, row, hide):
        self.table.setRowHidden(row, hide)

    def setColumnWidth(self, column, width):
        self.table.setColumnWidth(column, width)

    def get_export_data(self, columns):
        """
        Преобразует видимые строки таблицы в список словарей.

        Args:
            columns: Список имён столбцов (ключей словаря).

        Returns:
            list[dict]: Данные таблицы.
        """
        result = []
        for row in range(self.table.rowCount()):
            if self.table.isRowHidden(row):
                continue
            row_dict = {}
            for col, key in enumerate(columns):
                item = self.table.item(row, col)
                row_dict[key] = item.text() if item else ""
            result.append(row_dict)
        return result

