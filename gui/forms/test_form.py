

from PyQt5.QtWidgets import (
    QLabel, QLineEdit, QComboBox, QFormLayout, QMessageBox,
    QDateEdit, QPushButton, QHBoxLayout, QVBoxLayout, QWidget
)
from PyQt5.QtCore import Qt, QDate

from dao.test_execution_dao import TestExecutionDAO
from gui.forms.base_form import BaseForm


class TestForm(BaseForm):


    def __init__(self, test_id: int = None, parent=None):
        self.test_id = test_id
        self.test_execution_dao = TestExecutionDAO()
        self._entity = None

        super().__init__(parent)
        self.setWindowTitle("Редактирование испытания")
        self.setMinimumWidth(450)

        if self.test_id:
            self._load_entity()

    def _setup_ui(self):
        """Настраивает интерфейс."""
        layout = QFormLayout()

        self.lbl_serial = QLabel("Серийный номер изделия *")
        self.lbl_step = QLabel("Этап теста *")
        self.lbl_equipment = QLabel("Оборудование")
        self.lbl_start = QLabel("Дата начала")
        self.lbl_end = QLabel("Дата окончания")
        self.lbl_result = QLabel("Результат *")

        self.cb_serial = QComboBox()
        self._load_product_instances()

        self.cb_step = QComboBox()
        self._load_test_steps()

        self.cb_equipment = QComboBox()
        self.cb_equipment.addItem("— не назначено —", None)
        self._load_equipment()

        self.ed_start = QDateEdit()
        self.ed_start.setCalendarPopup(True)
        self.ed_start.setDate(QDate.currentDate())

        self.ed_end = QDateEdit()
        self.ed_end.setCalendarPopup(True)
        self.ed_end.setDate(QDate.currentDate())

        self.cb_result = QComboBox()
        self.cb_result.addItem("В процессе", "in_progress")
        self.cb_result.addItem("Пройдено", "passed")
        self.cb_result.addItem("Не пройдено", "failed")

        layout.addRow(self.lbl_serial, self.cb_serial)
        layout.addRow(self.lbl_step, self.cb_step)
        layout.addRow(self.lbl_equipment, self.cb_equipment)
        layout.addRow(self.lbl_start, self.ed_start)
        layout.addRow(self.lbl_end, self.ed_end)
        layout.addRow(self.lbl_result, self.cb_result)

        # Создаём основной layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.btn_save = QPushButton("Сохранить")
        self.btn_save.clicked.connect(self._on_save)
        button_layout.addWidget(self.btn_save)

        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_cancel)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def _load_product_instances(self):
        """Загружает экземпляры изделий."""
        try:
            from dao.product_instance_dao import ProductInstanceDAO
            instances = ProductInstanceDAO().get_all()
            for inst in instances:
                self.cb_serial.addItem(str(inst.serial_number), inst.serial_number)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить изделия: {e}")

    def _load_test_steps(self):
        """Загружает этапы тестов."""
        try:
            from db.connection import DatabaseConnection
            db = DatabaseConnection()
            conn = db.get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT ts.id_step, twl.test_name, e.name as equipment_name
                        FROM test_step ts
                        JOIN test_work_list twl ON ts.id_test_work = twl.id_test_work
                        LEFT JOIN equipment e ON twl.id_equipment = e.id_equipment
                        ORDER BY twl.test_name
                    """)
                    for row in cur.fetchall():
                        display = f"{row[1]}"
                        if row[2]:
                            display += f" ({row[2]})"
                        self.cb_step.addItem(display, row[0])
            finally:
                db.return_connection(conn)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить этапы: {e}")

    def _load_equipment(self):
        """Загружает оборудование."""
        try:
            from db.connection import DatabaseConnection
            db = DatabaseConnection()
            conn = db.get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT id_equipment, name FROM equipment ORDER BY name")
                    for row in cur.fetchall():
                        self.cb_equipment.addItem(row[1], row[0])
            finally:
                db.return_connection(conn)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить оборудование: {e}")

    def validate(self) -> bool:
        """Валидация данных."""
        if not self.cb_serial.currentData():
            QMessageBox.warning(self, "Ошибка", "Выберите изделие")
            return False
        if not self.cb_step.currentData():
            QMessageBox.warning(self, "Ошибка", "Выберите этап теста")
            return False
        if not self.cb_result.currentData():
            QMessageBox.warning(self, "Ошибка", "Выберите результат")
            return False
        if self.ed_start.date() > self.ed_end.date():
            QMessageBox.warning(self, "Ошибка", "Дата начала не может быть позже даты окончания")
            return False
        return True

    def save_entity(self):
        """Сохраняет испытание."""
        from models.test_execution import TestExecution

        if self.test_id:
            entity = self.test_execution_dao.get_by_id(self.test_id)
            if not entity:
                raise Exception("Испытание не найдено")
            entity.serial_number = self.cb_serial.currentData()
            entity.id_test_step = self.cb_step.currentData()
            entity.id_equipment = self.cb_equipment.currentData()
            entity.date_start = self.ed_start.date().toPyDate()
            entity.date_end = self.ed_end.date().toPyDate()
            entity.result = self.cb_result.currentData()
            self.test_execution_dao.update(entity)
        else:
            entity = TestExecution(
                serial_number=self.cb_serial.currentData(),
                id_test_step=self.cb_step.currentData(),
                id_equipment=self.cb_equipment.currentData(),
                date_start=self.ed_start.date().toPyDate(),
                date_end=self.ed_end.date().toPyDate(),
                result=self.cb_result.currentData()
            )
            self.test_execution_dao.insert(entity)

    def load_entity(self):
        """Загружает испытание в форму."""
        if not self.test_id:
            return

        entity = self.test_execution_dao.get_by_id(self.test_id)
        if not entity:
            raise Exception("Испытание не найдено")

        # Выбор изделия
        if entity.serial_number:
            for i in range(self.cb_serial.count()):
                if self.cb_serial.itemData(i) == entity.serial_number:
                    self.cb_serial.setCurrentIndex(i)
                    break

        # Выбор этапа
        if entity.id_test_step:
            for i in range(self.cb_step.count()):
                if self.cb_step.itemData(i) == entity.id_test_step:
                    self.cb_step.setCurrentIndex(i)
                    break

        # Выбор оборудования
        if entity.id_equipment:
            for i in range(self.cb_equipment.count()):
                if self.cb_equipment.itemData(i) == entity.id_equipment:
                    self.cb_equipment.setCurrentIndex(i)
                    break

        # Даты
        if entity.date_start:
            self.ed_start.setDate(QDate(entity.date_start.year, entity.date_start.month, entity.date_start.day))
        if entity.date_end:
            self.ed_end.setDate(QDate(entity.date_end.year, entity.date_end.month, entity.date_end.day))

        # Результат
        result_map = {"in_progress": 0, "passed": 1, "failed": 2}
        if entity.result in result_map:
            self.cb_result.setCurrentIndex(result_map[entity.result])
