

from PyQt5.QtWidgets import QLabel, QLineEdit, QComboBox, QFormLayout, QMessageBox
from PyQt5.QtCore import Qt

from db.connection import DatabaseConnection
from gui.forms.base_form import BaseForm
from utils.password_hasher import hash_password


class UserForm(BaseForm):


    def __init__(self, login: str = None, parent=None):
        self.login = login
        super().__init__(parent)
        self.setWindowTitle("Редактирование пользователя")
        self.setMinimumWidth(450)

        if self.login:
            self.load_entity()

    def _setup_ui(self):
        layout = QFormLayout()

        self.lbl_login = QLabel("Логин *")
        self.ed_login = QLineEdit()

        self.lbl_password = QLabel("Пароль *" if not self.login else "Пароль (оставьте пустым, чтобы не менять)")
        self.ed_password = QLineEdit()
        self.ed_password.setEchoMode(QLineEdit.Password)

        self.lbl_role = QLabel("Роль *")
        self.cb_role = QComboBox()
        roles = [
            ("Администратор", "admin"),
            ("Кадровик", "hr"),
            ("Начальник цеха", "shop_manager"),
            ("Мастер", "master"),
            ("Бригадир", "foreman"),
            ("Испытатель", "tester"),
            ("Технолог", "technologist"),
            ("Аналитик", "analyst"),
        ]
        for name, key in roles:
            self.cb_role.addItem(name, key)

        self.lbl_employee = QLabel("Сотрудник")
        self.cb_employee = QComboBox()
        self.cb_employee.addItem("— не назначен —", None)
        self._load_employees()

        layout.addRow(self.lbl_login, self.ed_login)
        layout.addRow(self.lbl_password, self.ed_password)
        layout.addRow(self.lbl_role, self.cb_role)
        layout.addRow(self.lbl_employee, self.cb_employee)
        self.form_layout.addLayout(layout)

        if self.login:
            self.ed_login.setReadOnly(True)

    def _load_employees(self):
        try:
            from dao.employee_dao import EmployeeDAO
            employees = EmployeeDAO().get_all()
            for emp in employees:
                self.cb_employee.addItem(
                    f"{emp.last_name} {emp.first_name}", emp.id_employee
                )
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить сотрудников: {e}")

    def validate(self) -> bool:
        if not self.login and not self.ed_login.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите логин")
            return False
        if not self.login and not self.ed_password.text():
            QMessageBox.warning(self, "Ошибка", "Введите пароль")
            return False
        if not self.cb_role.currentData():
            QMessageBox.warning(self, "Ошибка", "Выберите роль")
            return False
        return True

    def save_entity(self):
        db = DatabaseConnection()
        conn = db.get_connection()
        try:
            with conn.cursor() as cur:
                login = self.ed_login.text().strip()
                role = self.cb_role.currentData()
                id_employee = self.cb_employee.currentData()

                if self.login:
                    # Обновляем роль и сотрудника
                    cur.execute(
                        "UPDATE users SET role = %s, id_employee = %s WHERE login = %s",
                        (role, id_employee, self.login),
                    )
                    # Обновляем пароль, если введён
                    if self.ed_password.text():
                        password_hash = hash_password(self.ed_password.text())
                        cur.execute(
                            "UPDATE users SET password_hash = %s WHERE login = %s",
                            (password_hash, self.login),
                        )
                else:
                    password_hash = hash_password(self.ed_password.text())
                    cur.execute(
                        "INSERT INTO users (login, password_hash, role, id_employee) VALUES (%s, %s, %s, %s)",
                        (login, password_hash, role, id_employee),
                    )
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise Exception(f"Ошибка сохранения пользователя: {e}")
        finally:
            db.return_connection(conn)

    def load_entity(self):
        if not self.login:
            return

        db = DatabaseConnection()
        conn = db.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT login, role, id_employee FROM users WHERE login = %s",
                    (self.login,),
                )
                row = cur.fetchone()
                if not row:
                    raise Exception("Пользователь не найден")

                login, role, id_employee = row
                self.ed_login.setText(login)

                if role:
                    for i in range(self.cb_role.count()):
                        if self.cb_role.itemData(i) == role:
                            self.cb_role.setCurrentIndex(i)
                            break

                if id_employee:
                    for i in range(self.cb_employee.count()):
                        if self.cb_employee.itemData(i) == id_employee:
                            self.cb_employee.setCurrentIndex(i)
                            break
        finally:
            db.return_connection(conn)
