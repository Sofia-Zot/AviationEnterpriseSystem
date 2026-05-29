
from datetime import date
import logging
from PyQt5.QtWidgets import (
    QLabel, QLineEdit, QComboBox, QDateEdit, QGroupBox, QFormLayout,
    QMessageBox, QVBoxLayout, QRadioButton, QButtonGroup, QWidget, QHBoxLayout, QPushButton
)
from PyQt5.QtCore import Qt, QDate

from dao.employee_dao import EmployeeDAO
from dao.worker_dao import WorkerDAO
from dao.engineer_dao import EngineerDAO
from dao.tester_dao import TesterDAO
from dao.brigade_dao import BrigadeDAO
from gui.forms.base_form import BaseForm
from models.employee import Employee

logger = logging.getLogger(__name__)


class EmployeeForm(BaseForm):


    def __init__(self, employee_id: int = None, parent=None):
        self.employee_id = employee_id
        self.employee_dao = EmployeeDAO()
        self.worker_dao = WorkerDAO()
        self.engineer_dao = EngineerDAO()
        self.tester_dao = TesterDAO()

        self._entity = None
        self._current_type = "worker"

        super().__init__(parent)
        self.setWindowTitle("Редактирование сотрудника")
        self.setMinimumWidth(500)

        self._load_brigades()

        if self.employee_id:
            self._load_entity()

    def _setup_ui(self):
        """Настраивает интерфейс."""
        layout = QVBoxLayout()

        # Тип сотрудника
        type_group = QGroupBox("Тип сотрудника")
        type_layout = QVBoxLayout()

        self.type_group = QButtonGroup()
        self.rb_worker = QRadioButton("Рабочий")
        self.rb_engineer = QRadioButton("Инженер (ИТР)")
        self.rb_tester = QRadioButton("Испытатель")

        self.rb_worker.setChecked(True)
        self.rb_worker.toggled.connect(self._on_type_change)
        self.rb_engineer.toggled.connect(self._on_type_change)
        self.rb_tester.toggled.connect(self._on_type_change)

        self.type_group.addButton(self.rb_worker, 1)
        self.type_group.addButton(self.rb_engineer, 2)
        self.type_group.addButton(self.rb_tester, 3)

        type_layout.addWidget(self.rb_worker)
        type_layout.addWidget(self.rb_engineer)
        type_layout.addWidget(self.rb_tester)
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)

        # Общие поля
        general_group = QGroupBox("Общие данные")
        self.general_layout = QFormLayout()

        self.lbl_last_name = QLabel("Фамилия *")
        self.lbl_first_name = QLabel("Имя *")
        self.lbl_middle_name = QLabel("Отчество")
        self.lbl_birth_date = QLabel("Дата рождения")
        self.lbl_education = QLabel("Образование")
        self.lbl_hire_date = QLabel("Дата приёма *")
        self.lbl_prior_exp = QLabel("Предыдущий опыт (лет)")
        self.lbl_address = QLabel("Адрес")
        self.lbl_phone = QLabel("Телефон")
        self.lbl_salary = QLabel("Зарплата")

        self.ed_last_name = QLineEdit()
        self.ed_first_name = QLineEdit()
        self.ed_middle_name = QLineEdit()
        self.ed_birth_date = QDateEdit()
        self.ed_birth_date.setCalendarPopup(True)
        self.ed_birth_date.setDate(QDate.currentDate())
        self.ed_education = QLineEdit()
        self.ed_hire_date = QDateEdit()
        self.ed_hire_date.setCalendarPopup(True)
        self.ed_hire_date.setDate(QDate.currentDate())
        self.ed_prior_exp = QLineEdit()
        self.ed_address = QLineEdit()
        self.ed_phone = QLineEdit()
        self.ed_salary = QLineEdit()

        self.general_layout.addRow(self.lbl_last_name, self.ed_last_name)
        self.general_layout.addRow(self.lbl_first_name, self.ed_first_name)
        self.general_layout.addRow(self.lbl_middle_name, self.ed_middle_name)
        self.general_layout.addRow(self.lbl_birth_date, self.ed_birth_date)
        self.general_layout.addRow(self.lbl_education, self.ed_education)
        self.general_layout.addRow(self.lbl_hire_date, self.ed_hire_date)
        self.general_layout.addRow(self.lbl_prior_exp, self.ed_prior_exp)
        self.general_layout.addRow(self.lbl_address, self.ed_address)
        self.general_layout.addRow(self.lbl_phone, self.ed_phone)
        self.general_layout.addRow(self.lbl_salary, self.ed_salary)

        general_group.setLayout(self.general_layout)
        layout.addWidget(general_group)

        # Специфичные поля для рабочих
        self.worker_group = QGroupBox("Данные рабочего")
        worker_layout = QFormLayout()

        self.lbl_profession = QLabel("Профессия *")
        self.lbl_rank = QLabel("Разряд (1-6) *")
        self.lbl_id_brigade = QLabel("Бригада")

        self.ed_profession = QLineEdit()
        self.ed_rank = QLineEdit()
        self.cb_brigade = QComboBox()

        worker_layout.addRow(self.lbl_profession, self.ed_profession)
        worker_layout.addRow(self.lbl_rank, self.ed_rank)
        worker_layout.addRow(self.lbl_id_brigade, self.cb_brigade)

        self.worker_group.setLayout(worker_layout)
        layout.addWidget(self.worker_group)

        # Специфичные поля для инженеров
        self.engineer_group = QGroupBox("Данные инженера")
        engineer_layout = QFormLayout()

        self.lbl_position = QLabel("Должность *")
        self.lbl_section = QLabel("Участок")

        self.ed_position = QLineEdit()
        self.cb_section = QComboBox()
        self._load_sections()

        engineer_layout.addRow(self.lbl_position, self.ed_position)
        engineer_layout.addRow(self.lbl_section, self.cb_section)

        self.engineer_group.setLayout(engineer_layout)
        layout.addWidget(self.engineer_group)

        # Специфичные поля для испытателей
        self.tester_group = QGroupBox("Данные испытателя")
        tester_layout = QFormLayout()

        self.lbl_specialization = QLabel("Специализация *")
        self.lbl_lab = QLabel("Лаборатория")

        self.ed_specialization = QLineEdit()
        self.cb_lab = QComboBox()
        self._load_labs()

        tester_layout.addRow(self.lbl_specialization, self.ed_specialization)
        tester_layout.addRow(self.lbl_lab, self.cb_lab)

        self.tester_group.setLayout(tester_layout)
        layout.addWidget(self.tester_group)

        # По умолчанию показываем только рабочего
        self._on_type_change()

        layout.addStretch()

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.btn_save = QPushButton("Сохранить")
        self.btn_save.clicked.connect(self._on_save)
        button_layout.addWidget(self.btn_save)

        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_cancel)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _load_sections(self):
        """Загружает участки."""
        try:
            from db.connection import DatabaseConnection
            db = DatabaseConnection()
            conn = db.get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT id_section, name FROM section ORDER BY name")
                    for row in cur.fetchall():
                        self.cb_section.addItem(row[1], row[0])
            finally:
                db.return_connection(conn)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить участки: {e}")

    def _load_labs(self):
        """Загружает лаборатории."""
        try:
            from db.connection import DatabaseConnection
            db = DatabaseConnection()
            conn = db.get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT id_lab, name FROM laboratory ORDER BY name")
                    for row in cur.fetchall():
                        self.cb_lab.addItem(row[1], row[0])
            finally:
                db.return_connection(conn)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить лаборатории: {e}")

    def _load_brigades(self):
        """Загружает бригады."""
        self.cb_brigade.clear()
        try:
            from dao.brigade_dao import BrigadeDAO
            brigades = BrigadeDAO().get_all()
            for b in brigades:
                self.cb_brigade.addItem(b.name, b.id_brigade)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить бригады: {e}")

    def _on_type_change(self):
        """Показывает/скрывает поля в зависимости от типа."""
        if self.rb_worker.isChecked():
            self._current_type = "worker"
            self.worker_group.setVisible(True)
            self.engineer_group.setVisible(False)
            self.tester_group.setVisible(False)
        elif self.rb_engineer.isChecked():
            self._current_type = "engineer"
            self.worker_group.setVisible(False)
            self.engineer_group.setVisible(True)
            self.tester_group.setVisible(False)
        else:
            self._current_type = "tester"
            self.worker_group.setVisible(False)
            self.engineer_group.setVisible(False)
            self.tester_group.setVisible(True)

    def validate(self) -> bool:
        """Валидация данных."""
        if not self.ed_last_name.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите фамилию")
            return False
        if not self.ed_first_name.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите имя")
            return False
        if not self.ed_hire_date.text():
            QMessageBox.warning(self, "Ошибка", "Выберите дату приёма")
            return False

        if self._current_type == "worker":
            if not self.ed_profession.text().strip():
                QMessageBox.warning(self, "Ошибка", "Введите профессию")
                return False
            try:
                rank = int(self.ed_rank.text())
                if rank < 1 or rank > 6:
                    QMessageBox.warning(self, "Ошибка", "Разряд должен быть от 1 до 6")
                    return False
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Введите корректный разряд")
                return False

        elif self._current_type == "engineer":
            if not self.ed_position.text().strip():
                QMessageBox.warning(self, "Ошибка", "Введите должность")
                return False

        elif self._current_type == "tester":
            if not self.ed_specialization.text().strip():
                QMessageBox.warning(self, "Ошибка", "Введите специализацию")
                return False

        return True

    def save_entity(self):
        """Сохраняет сотрудника."""
        from db.connection import DatabaseConnection

        # Сохраняем общие данные
        if self.employee_id:
            entity = self.employee_dao.get_by_id(self.employee_id)
            if not entity:
                raise Exception("Сотрудник не найден")
        else:
            entity = Employee()

        entity.last_name = self.ed_last_name.text().strip()
        entity.first_name = self.ed_first_name.text().strip()
        entity.middle_name = self.ed_middle_name.text().strip()
        entity.birth_date = self.ed_birth_date.date().toPyDate()
        entity.education = self.ed_education.text().strip()
        entity.hire_date = self.ed_hire_date.date().toPyDate()
        entity.prior_exp = int(self.ed_prior_exp.text()) if self.ed_prior_exp.text() else None
        entity.address = self.ed_address.text().strip()
        entity.phone = self.ed_phone.text().strip()
        entity.salary = float(self.ed_salary.text()) if self.ed_salary.text() else None

        if self.employee_id:
            self.employee_dao.update(entity)
        else:
            self.employee_dao.insert(entity)
            self.employee_id = entity.id_employee

        # Сохраняем специфичные данные
        if self._current_type == "worker":
            new_brigade_id = self.cb_brigade.currentData() if self.cb_brigade.currentData() else None
            worker = self.worker_dao.get_by_id(self.employee_id)
            
            if worker:
                old_brigade_id = worker.id_brigade
                worker.profession = self.ed_profession.text().strip()
                worker.rank = int(self.ed_rank.text())
                worker.id_brigade = new_brigade_id
                worker.is_foreman = worker.is_foreman if worker.is_foreman else False
                
                # Если рабочий был бригадиром и меняет бригаду - снимаем с должности
                if worker.is_foreman and old_brigade_id != new_brigade_id:
                    # Сбрасываем бригаду у сотрудника
                    worker.is_foreman = False
                    
                    # Обновляем бригаду: id_foreman = NULL
                    if old_brigade_id:
                        db = DatabaseConnection()
                        conn = db.get_connection()
                        try:
                            with conn.cursor() as cur:
                                cur.execute(
                                    "UPDATE brigade SET id_foreman = NULL WHERE id_brigade = %s",
                                    (old_brigade_id,)
                                )
                            conn.commit()
                        finally:
                            db.return_connection(conn)
                
                self.worker_dao.update(worker)
            else:
                worker_data = {
                    'id_employee': self.employee_id,
                    'profession': self.ed_profession.text().strip(),
                    'rank': int(self.ed_rank.text()),
                    'is_foreman': False,
                    'id_brigade': new_brigade_id
                }
                from models.worker import Worker
                worker = Worker(**worker_data)
                self.worker_dao.insert(worker)

        elif self._current_type == "engineer":
            engineer = self.engineer_dao.get_by_id(self.employee_id)
            if engineer:
                engineer.position = self.ed_position.text().strip()
                engineer.id_section = self.cb_section.currentData() if self.cb_section.currentData() else None
                self.engineer_dao.update(engineer)
            else:
                from models.engineer import Engineer
                engineer = Engineer(
                    id_employee=self.employee_id,
                    position=self.ed_position.text().strip(),
                    id_section=self.cb_section.currentData() if self.cb_section.currentData() else None
                )
                self.engineer_dao.insert(engineer)

        elif self._current_type == "tester":
            tester = self.tester_dao.get_by_id(self.employee_id)
            if tester:
                tester.specialization = self.ed_specialization.text().strip()
                tester.id_lab = self.cb_lab.currentData() if self.cb_lab.currentData() else None
                self.tester_dao.update(tester)
            else:
                from models.tester import Tester
                tester = Tester(
                    id_employee=self.employee_id,
                    specialization=self.ed_specialization.text().strip(),
                    id_lab=self.cb_lab.currentData() if self.cb_lab.currentData() else None
                )
                self.tester_dao.insert(tester)

    def load_entity(self):
        """Загружает сотрудника в форму."""
        if not self.employee_id:
            return

        entity = self.employee_dao.get_by_id(self.employee_id)
        if not entity:
            raise Exception("Сотрудник не найден")

        self.ed_last_name.setText(entity.last_name or "")
        self.ed_first_name.setText(entity.first_name or "")
        self.ed_middle_name.setText(entity.middle_name or "")
        if entity.birth_date:
            self.ed_birth_date.setDate(QDate(entity.birth_date.year, entity.birth_date.month, entity.birth_date.day))
        self.ed_education.setText(entity.education or "")
        if entity.hire_date:
            self.ed_hire_date.setDate(QDate(entity.hire_date.year, entity.hire_date.month, entity.hire_date.day))
        if entity.prior_exp:
            self.ed_prior_exp.setText(str(entity.prior_exp))
        self.ed_address.setText(entity.address or "")
        self.ed_phone.setText(entity.phone or "")
        if entity.salary:
            self.ed_salary.setText(str(entity.salary))

        # Загружаем специфичные данные
        try:
            worker = self.worker_dao.get_by_id(self.employee_id)
            if worker:
                self.rb_worker.setChecked(True)
                self.ed_profession.setText(worker.profession or "")
                self.ed_rank.setText(str(worker.rank))
                if worker.id_brigade:
                    self._load_brigades()
                    for i in range(self.cb_brigade.count()):
                        if self.cb_brigade.itemData(i) == worker.id_brigade:
                            self.cb_brigade.setCurrentIndex(i)
                            break
                self._on_type_change()
                return
        except:
            pass

        try:
            engineer = self.engineer_dao.get_by_id(self.employee_id)
            if engineer:
                self.rb_engineer.setChecked(True)
                self.ed_position.setText(engineer.position or "")
                if engineer.id_section:
                    for i in range(self.cb_section.count()):
                        if self.cb_section.itemData(i) == engineer.id_section:
                            self.cb_section.setCurrentIndex(i)
                            break
                self._on_type_change()
                return
        except:
            pass

        try:
            tester = self.tester_dao.get_by_id(self.employee_id)
            if tester:
                self.rb_tester.setChecked(True)
                self.ed_specialization.setText(tester.specialization or "")
                if tester.id_lab:
                    for i in range(self.cb_lab.count()):
                        if self.cb_lab.itemData(i) == tester.id_lab:
                            self.cb_lab.setCurrentIndex(i)
                            break
                self._on_type_change()
                return
        except:
            pass
