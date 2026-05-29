

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QHeaderView,
    QWidget,
    QAbstractItemView,
    QFileDialog,
)
from PyQt5.QtCore import Qt

from db.connection import DatabaseConnection
from gui.forms.user_form import UserForm
from gui.widgets.filtered_table import FilteredTable
from services.report_service import ReportService


class UserListDialog(QDialog):


    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_users()

    def _setup_ui(self):
        self.setWindowTitle("Пользователи")
        self.setMinimumSize(700, 450)

        layout = QVBoxLayout()

        # Таблица
        self.table = FilteredTable()
        self.table.set_headers(["Логин", "Роль", "Сотрудник", "Действия"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
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

        self.btn_export = QPushButton("Экспорт CSV")
        self.btn_export.clicked.connect(self._on_export)
        button_layout.addWidget(self.btn_export)

        self.btn_close = QPushButton("Закрыть")
        self.btn_close.clicked.connect(self.close)
        button_layout.addWidget(self.btn_close)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _load_users(self):
        self.table.clear()
        db = DatabaseConnection()
        conn = db.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT u.login, u.role,
                           e.last_name, e.first_name, e.middle_name
                    FROM users u
                    LEFT JOIN employee e ON u.id_employee = e.id_employee
                    ORDER BY u.login
                    """
                )
                rows = cur.fetchall()
                for row in rows:
                    login, role, last_name, first_name, middle_name = row
                    emp_name = (
                        f"{last_name or ''} {first_name or ''} {middle_name or ''}".strip()
                        or "—"
                    )
                    self.table.add_row([login, role, emp_name], row_data=login)
                    pos = self.table.rowCount() - 1

                    btn_widget = QWidget()
                    btn_layout = QHBoxLayout()
                    btn_layout.setContentsMargins(0, 0, 0, 0)

                    btn_edit = QPushButton("✏️")
                    btn_edit.setToolTip("Редактировать")
                    btn_edit.clicked.connect(lambda checked, l=login: self._edit_user(l))
                    btn_layout.addWidget(btn_edit)

                    btn_del = QPushButton("🗑️")
                    btn_del.setToolTip("Удалить")
                    btn_del.clicked.connect(lambda checked, l=login: self._delete_user(l))
                    btn_layout.addWidget(btn_del)

                    btn_widget.setLayout(btn_layout)
                    self.table.setCellWidget(pos, 3, btn_widget)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить пользователей: {e}")
        finally:
            db.return_connection(conn)

    def _on_add(self):
        form = UserForm(parent=self)
        if form.exec_() == UserForm.Accepted:
            self._load_users()

    def _on_edit(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите пользователя для редактирования")
            return

        login = self.table.item(self.table.currentRow(), 0).text()
        self._edit_user(login)

    def _edit_user(self, login):
        form = UserForm(login=login, parent=self)
        if form.exec_() == UserForm.Accepted:
            self._load_users()

    def _on_delete(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите пользователя для удаления")
            return

        login = self.table.item(self.table.currentRow(), 0).text()
        self._delete_user(login)

    def _delete_user(self, login):
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить пользователя '{login}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                db = DatabaseConnection()
                conn = db.get_connection()
                try:
                    with conn.cursor() as cur:
                        cur.execute("DELETE FROM users WHERE login = %s", (login,))
                        conn.commit()
                        deleted = cur.rowcount == 1
                finally:
                    db.return_connection(conn)

                if deleted:
                    self._load_users()
                    QMessageBox.information(self, "Успех", "Пользователь удалён")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить пользователя")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {e}")

    def _on_export(self):
        """Экспортирует данные таблицы в CSV."""
        try:
            data = self.table.get_export_data(["Логин", "Роль", "Сотрудник"])
            filename, _ = QFileDialog.getSaveFileName(
                self, "Сохранить CSV", "users.csv", "CSV (*.csv)"
            )
            if filename:
                ReportService.export_to_csv(data, filename)
                QMessageBox.information(self, "Успех", f"Данные экспортированы в {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать: {e}")

