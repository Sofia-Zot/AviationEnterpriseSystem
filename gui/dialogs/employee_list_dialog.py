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
    QLineEdit,
    QWidget,
)
from PyQt5.QtCore import Qt

from dao.employee_dao import EmployeeDAO
from gui.forms.employee_form import EmployeeForm


class EmployeeListDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.employee_dao = EmployeeDAO()
        self._setup_ui()
        self._load_employees()

    def _setup_ui(self):
        """Настраивает интерфейс."""
        self.setWindowTitle("Сотрудники")
        self.setMinimumSize(900, 500)

        layout = QVBoxLayout()

        # Фильтры
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Поиск:"))

        self.ed_search = QLineEdit()
        self.ed_search.setPlaceholderText("ФИО...")
        self.ed_search.textChanged.connect(self._on_filter)
        filter_layout.addWidget(self.ed_search)

        filter_layout.addWidget(QLabel("Тип:"))
        self.cb_type_filter = QComboBox()
        self.cb_type_filter.addItem("Все", "all")
        self.cb_type_filter.addItem("Рабочий", "worker")
        self.cb_type_filter.addItem("Инженер", "engineer")
        self.cb_type_filter.addItem("Испытатель", "tester")
        self.cb_type_filter.currentIndexChanged.connect(self._on_filter)
        filter_layout.addWidget(self.cb_type_filter)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Фамилия", "Имя", "Отчество", "Тип", "Действия"
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

    def _load_employees(self):
        """Загружает сотрудников в таблицу."""
        self.table.setRowCount(0)

        try:
            employees = self.employee_dao.get_all()
            for emp in employees:
                pos = self.table.rowCount()
                self.table.insertRow(pos)

                self.table.setItem(pos, 0, QTableWidgetItem(str(emp.id_employee)))
                self.table.setItem(pos, 1, QTableWidgetItem(emp.last_name or ""))
                self.table.setItem(pos, 2, QTableWidgetItem(emp.first_name or ""))
                self.table.setItem(pos, 3, QTableWidgetItem(emp.middle_name or ""))

                # Определение типа
                emp_type = self._get_employee_type(emp.id_employee)
                self.table.setItem(pos, 4, QTableWidgetItem(emp_type))

                # Кнопки действий
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(0, 0, 0, 0)

                btn_edit = QPushButton("✏️")
                btn_edit.setToolTip("Редактировать")
                btn_edit.clicked.connect(lambda checked, id=emp.id_employee: self._edit_employee(id))
                btn_layout.addWidget(btn_edit)

                btn_del = QPushButton("🗑️")
                btn_del.setToolTip("Удалить")
                btn_del.clicked.connect(lambda checked, id=emp.id_employee: self._delete_employee(id))
                btn_layout.addWidget(btn_del)

                btn_widget.setLayout(btn_layout)
                self.table.setCellWidget(pos, 5, btn_widget)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить сотрудников: {e}")

    def _get_employee_type(self, id_employee):
        """Определяет тип сотрудника."""
        try:
            from dao.worker_dao import WorkerDAO
            if WorkerDAO().get_by_id(id_employee):
                return "Рабочий"
        except:
            pass

        try:
            from dao.engineer_dao import EngineerDAO
            if EngineerDAO().get_by_id(id_employee):
                return "Инженер"
        except:
            pass

        try:
            from dao.tester_dao import TesterDAO
            if TesterDAO().get_by_id(id_employee):
                return "Испытатель"
        except:
            pass

        return "—"

    def _on_filter(self, text=None):
        """Фильтрует таблицу."""
        search = self.ed_search.text().lower()
        type_filter = self.cb_type_filter.currentData()

        for row in range(self.table.rowCount()):
            name_match = True
            if search:
                last_name = self.table.item(row, 1).text().lower() if self.table.item(row, 1) else ""
                first_name = self.table.item(row, 2).text().lower() if self.table.item(row, 2) else ""
                middle_name = self.table.item(row, 3).text().lower() if self.table.item(row, 3) else ""
                name_match = search in last_name or search in first_name or search in middle_name

            type_match = True
            if type_filter != "all":
                type_map = {"worker": "Рабочий", "engineer": "Инженер", "tester": "Испытатель"}
                expected = type_map.get(type_filter, "")
                actual = self.table.item(row, 4).text() if self.table.item(row, 4) else ""
                type_match = expected == actual

            self.table.setRowHidden(row, not (name_match and type_match))

    def _on_add(self):
        """Открывает форму добавления."""
        form = EmployeeForm(parent=self)
        if form.exec_() == EmployeeForm.Accepted:
            self._load_employees()

    def _on_edit(self):
        """Открывает форму редактирования."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите сотрудника для редактирования")
            return

        emp_id = int(self.table.item(self.table.currentRow(), 0).text())
        self._edit_employee(emp_id)

    def _edit_employee(self, employee_id):
        """Открывает форму редактирования."""
        form = EmployeeForm(employee_id=employee_id, parent=self)
        if form.exec_() == EmployeeForm.Accepted:
            self._load_employees()

    def _on_delete(self):
        """Удаляет выбранную строку."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите сотрудника для удаления")
            return

        emp_id = int(self.table.item(self.table.currentRow(), 0).text())
        self._delete_employee(emp_id)

    def _delete_employee(self, employee_id):
        """Удаляет сотрудника."""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены, что хотите удалить сотрудника ID={employee_id}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                success = self.employee_dao.delete(employee_id)
                if success:
                    self._load_employees()
                    QMessageBox.information(self, "Успех", "Сотрудник удалён")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить (возможно, есть связанные данные)")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {e}")
