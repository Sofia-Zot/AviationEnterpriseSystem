

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QMessageBox,
    QHeaderView,
    QComboBox,
    QLabel,
    QWidget,
)
from PyQt5.QtCore import Qt

from dao.test_execution_dao import TestExecutionDAO
from gui.forms.test_form import TestForm


class TestListDialog(QDialog):


    def __init__(self, parent=None):
        super().__init__(parent)
        self.test_execution_dao = TestExecutionDAO()
        self._setup_ui()
        self._load_tests()

    def _setup_ui(self):
        """Настраивает интерфейс."""
        self.setWindowTitle("Испытания")
        self.setMinimumSize(900, 500)

        layout = QVBoxLayout()

        # Фильтры
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Статус:"))

        self.cb_result_filter = QComboBox()
        self.cb_result_filter.addItem("Все", "all")
        self.cb_result_filter.addItem("Пройдено", "passed")
        self.cb_result_filter.addItem("Не пройдено", "failed")
        self.cb_result_filter.addItem("В процессе", "in_progress")
        self.cb_result_filter.currentIndexChanged.connect(self._on_filter)
        filter_layout.addWidget(self.cb_result_filter)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Изделие", "Этап", "Оборудование", "Результат", "Действия"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.table)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.btn_add = QPushButton("Добавить")
        self.btn_add.clicked.connect(self._on_add)
        button_layout.addWidget(self.btn_add)

        self.btn_edit = QPushButton("Редактировать")
        self.btn_edit.clicked.connect(self._on_edit)
        button_layout.addWidget(self.btn_edit)

        self.btn_delete = QPushButton("Удалить")
        self.btn_delete.clicked.connect(self._on_delete)
        button_layout.addWidget(self.btn_delete)

        self.btn_close = QPushButton("Закрыть")
        self.btn_close.clicked.connect(self.close)
        button_layout.addWidget(self.btn_close)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _load_tests(self):
        """Загружает испытания в таблицу."""
        self.table.setRowCount(0)

        try:
            tests = self.test_execution_dao.get_all()
            for test in tests:
                pos = self.table.rowCount()
                self.table.insertRow(pos)

                self.table.setItem(pos, 0, QTableWidgetItem(str(test.id_test_execution)))
                self.table.setItem(pos, 1, QTableWidgetItem(str(test.serial_number)))
                self.table.setItem(pos, 2, QTableWidgetItem(test.test_step_name or "-"))
                self.table.setItem(pos, 3, QTableWidgetItem(test.equipment_name or "-"))
                self.table.setItem(pos, 4, QTableWidgetItem(self._format_result(test.result)))

                # Кнопки действий
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(0, 0, 0, 0)

                btn_edit = QPushButton("✏️")
                btn_edit.setToolTip("Редактировать")
                btn_edit.clicked.connect(lambda checked, id=test.id_test_execution: self._edit_test(id))
                btn_layout.addWidget(btn_edit)

                btn_del = QPushButton("🗑️")
                btn_del.setToolTip("Удалить")
                btn_del.clicked.connect(lambda checked, id=test.id_test_execution: self._delete_test(id))
                btn_layout.addWidget(btn_del)

                btn_widget.setLayout(btn_layout)
                self.table.setCellWidget(pos, 5, btn_widget)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить испытания: {e}")

    def _format_result(self, result):
        """Форматирует результат."""
        results = {
            'passed': 'Пройдено',
            'failed': 'Не пройдено',
            'in_progress': 'В процессе',
        }
        return results.get(result, result)

    def _on_filter(self, index):
        """Фильтрует таблицу по результату."""
        result = self.cb_result_filter.currentData()

        for row in range(self.table.rowCount()):
            if result == "all":
                self.table.setRowHidden(row, False)
            else:
                result_item = self.table.item(row, 4)
                self.table.setRowHidden(row, result_item and result_item.text() != self._format_result(result))

    def _on_add(self):
        """Открывает форму добавления."""
        form = TestForm(parent=self)
        if form.exec_() == TestForm.Accepted:
            self._load_tests()

    def _on_edit(self):
        """Открывает форму редактирования."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите испытание для редактирования")
            return

        test_id = int(self.table.item(self.table.currentRow(), 0).text())
        self._edit_test(test_id)

    def _edit_test(self, test_id):
        """Открывает форму редактирования."""
        form = TestForm(test_id=test_id, parent=self)
        if form.exec_() == TestForm.Accepted:
            self._load_tests()

    def _on_delete(self):
        """Удаляет выбранную строку."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите испытание для удаления")
            return

        test_id = int(self.table.item(self.table.currentRow(), 0).text())
        self._delete_test(test_id)

    def _delete_test(self, test_id):
        """Удаляет испытание."""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены, что хотите удалить испытание ID={test_id}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                success = self.test_execution_dao.delete(test_id)
                if success:
                    self._load_tests()
                    QMessageBox.information(self, "Успех", "Испытание удалено")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {e}")
