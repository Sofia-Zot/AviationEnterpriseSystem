
import csv
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QMessageBox,
    QFileDialog,
    QLineEdit, QStatusBar,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from dao.query_dao import QueryDAO
from utils.logger import get_logger

logger = get_logger()


class BaseQueryWindow(QDialog):


    def __init__(self, query_dao: QueryDAO, parent=None):
        """
        Args:
            query_dao: Экземпляр QueryDAO для выполнения запросов.
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self.query_dao = query_dao
        self._setup_ui()

    def _setup_ui(self):
        """Настраивает базовый интерфейс."""
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout()

        # Заголовок
        self.title_label = QLabel(self._get_title())
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)

        # Контейнер для параметров (переопределяется в наследниках)
        self.params_widget = self._create_params_widget()
        if self.params_widget:
            layout.addWidget(self.params_widget)

        # Таблица результатов
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ccc;
                selection-background-color: #d0e1f9;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        layout.addWidget(self.table)

        # Панель кнопок
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.btn_execute = QPushButton("Выполнить")
        self.btn_execute.clicked.connect(self._on_execute)
        button_layout.addWidget(self.btn_execute)

        self.btn_export = QPushButton("Экспорт в CSV")
        self.btn_export.clicked.connect(self._on_export)
        button_layout.addWidget(self.btn_export)

        self.btn_close = QPushButton("Закрыть")
        self.btn_close.clicked.connect(self.close)
        button_layout.addWidget(self.btn_close)

        layout.addLayout(button_layout)

        # Статусная строка
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Готов к работе")
        layout.addWidget(self.status_bar)

        self.setLayout(layout)

    def _get_title(self) -> str:
        """Возвращает заголовок окна (переопределяется в наследниках)."""
        return "Запрос"

    def _create_params_widget(self) -> QWidget:
        """
        Создаёт виджет с параметрами фильтрации (переопределяется в наследниках).

        Returns:
            QWidget или None если параметров нет.
        """
        return None

    def _on_execute(self):
        """Обработчик кнопки "Выполнить"."""
        try:
            logger.info("Выполнение запроса: %s", self._get_title())
            self.status_bar.showMessage("Выполнение запроса...")
            self.table.setRowCount(0)
            self._execute_query()
            logger.info("Запрос выполнен успешно: %s строк", self.table.rowCount())
        except Exception as e:
            logger.exception("Ошибка в %s: %s", self._get_title(), str(e))
            QMessageBox.critical(self, "Ошибка выполнения", str(e))
            self.status_bar.showMessage("Ошибка")

    def _execute_query(self):
        """
        Выполняет запрос и отображает результаты (переопределяется в наследниках).
        """
        raise NotImplementedError("Метод _execute_query должен быть реализован в наследнике")

    def display_results(self, data, columns: list = None):
        """
        Отображает результаты в таблице.

        Args:
            data: Список словарей или список кортежей.
            columns: Список названий колонок (если None, берётся из данных).
        """
        if not data:
            self.status_bar.showMessage("Данных не найдено")
            self.table.setRowCount(0)
            return

        # Определяем колонки
        if columns is None:
            if isinstance(data[0], dict):
                columns = list(data[0].keys())
            else:
                columns = [f"Колонка {i+1}" for i in range(len(data[0]))]

        # Настраиваем таблицу
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setRowCount(len(data))

        # Заполняем данные
        for row_idx, row_data in enumerate(data):
            if isinstance(row_data, dict):
                # Если columns — русские заголовки, а не ключи словаря,
                # используем значения словаря по порядку
                if columns[0] not in row_data:
                    values = list(row_data.values())
                else:
                    values = [row_data.get(col, "") for col in columns]
            else:
                values = list(row_data)

            for col_idx, value in enumerate(values):
                item = QTableWidgetItem(str(value) if value is not None else "")
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

        # Автоподстройка ширины колонок
        self.table.resizeColumnsToContents()

        self.status_bar.showMessage(f"Найдено записей: {len(data)}")

    def _on_export(self):
        """Экспорт результатов в CSV (опционально)."""
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "Экспорт", "Нет данных для экспорта")
            return

        # Простая реализация экспорта (можно улучшить)
        from PyQt5.QtWidgets import QFileDialog
        import csv

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт в CSV", "", "CSV Files (*.csv)"
        )

        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';')

                    # Заголовки
                    headers = []
                    for col in range(self.table.columnCount()):
                        headers.append(self.table.horizontalHeaderItem(col).text())
                    writer.writerow(headers)

                    # Данные
                    for row in range(self.table.rowCount()):
                        row_data = []
                        for col in range(self.table.columnCount()):
                            item = self.table.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)

                QMessageBox.information(self, "Экспорт", f"Данные сохранены в:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка экспорта", str(e))

    def _set_row_color(self, row_idx: int, color: str = "#f0f0f0"):
        """Подсвечивает строку заданным цветом."""
        for col in range(self.table.columnCount()):
            item = self.table.item(row_idx, col)
            if item:
                item.setBackground(QColor(color))
