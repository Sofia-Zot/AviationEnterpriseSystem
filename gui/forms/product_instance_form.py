
import logging
from PyQt5.QtWidgets import (
    QLabel, QLineEdit, QComboBox, QFormLayout, QMessageBox,
    QVBoxLayout, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt

from dao.product_instance_dao import ProductInstanceDAO
from gui.forms.base_form import BaseForm

logger = logging.getLogger(__name__)


class ProductInstanceForm(BaseForm):


    def __init__(self, serial_number: int = None, parent=None):
        self.serial_number = serial_number
        self.product_instance_dao = ProductInstanceDAO()
        self._entity = None

        super().__init__(parent)
        self.setWindowTitle("Редактирование изделия")
        self.setMinimumWidth(450)

        if self.serial_number:
            self._load_entity()

    def _setup_ui(self):
        """Настраивает интерфейс."""
        layout = QFormLayout()

        self.lbl_serial = QLabel("Серийный номер *")
        self.lbl_type = QLabel("Тип изделия *")
        self.lbl_status = QLabel("Статус *")
        self.lbl_shop = QLabel("Цех")
        self.lbl_weight = QLabel("Вес (кг)")
        self.lbl_material = QLabel("Материал")
        self.lbl_batch = QLabel("Партия")

        self.ed_serial = QLineEdit()
        self.ed_serial.setReadOnly(bool(self.serial_number))  # Нельзя менять при редактировании

        self.cb_type = QComboBox()
        self._load_product_types()

        self.cb_status = QComboBox()
        self.cb_status.addItem("В сборке", "in_assembly")
        self.cb_status.addItem("На испытаниях", "under_test")
        self.cb_status.addItem("Готово", "ready")

        self.cb_shop = QComboBox()
        self._load_shops()

        self.ed_weight = QLineEdit()
        self.ed_material = QLineEdit()
        self.ed_batch = QLineEdit()

        layout.addRow(self.lbl_serial, self.ed_serial)
        layout.addRow(self.lbl_type, self.cb_type)
        layout.addRow(self.lbl_status, self.cb_status)
        layout.addRow(self.lbl_shop, self.cb_shop)
        layout.addRow(self.lbl_weight, self.ed_weight)
        layout.addRow(self.lbl_material, self.ed_material)
        layout.addRow(self.lbl_batch, self.ed_batch)

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

    def _load_product_types(self):
        """Загружает типы изделий."""
        try:
            from dao.product_type_dao import ProductTypeDAO
            types = ProductTypeDAO().get_all()
            for t in types:
                self.cb_type.addItem(t.name, t.id_type)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить типы: {e}")

    def _load_shops(self):
        """Загружает цеха."""
        try:
            from db.connection import DatabaseConnection
            db = DatabaseConnection()
            conn = db.get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT id_shop, name FROM shop ORDER BY name")
                    for row in cur.fetchall():
                        self.cb_shop.addItem(row[1], row[0])
            finally:
                db.return_connection(conn)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить цеха: {e}")

    def validate(self) -> bool:
        """Валидация данных."""
        if not self.ed_serial.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите серийный номер")
            return False
        if not self.cb_type.currentData():
            QMessageBox.warning(self, "Ошибка", "Выберите тип изделия")
            return False
        if not self.cb_status.currentData():
            QMessageBox.warning(self, "Ошибка", "Выберите статус")
            return False
        return True

    def save_entity(self):
        """Сохраняет изделие."""
        from models.product_instance import ProductInstance

        if self.serial_number:
            entity = self.product_instance_dao.get_by_serial(self.serial_number)
            if not entity:
                raise Exception("Изделие не найдено")
            entity.status = self.cb_status.currentData()
            entity.id_shop = self.cb_shop.currentData() if self.cb_shop.currentData() else None
            entity.weight = float(self.ed_weight.text()) if self.ed_weight.text() else None
            entity.material = self.ed_material.text().strip()
            entity.batch = self.ed_batch.text().strip()
            self.product_instance_dao.update(entity)
        else:
            entity = ProductInstance(
                serial_number=int(self.ed_serial.text()),
                id_type=self.cb_type.currentData(),
                status=self.cb_status.currentData(),
                id_shop=self.cb_shop.currentData() if self.cb_shop.currentData() else None,
                weight=float(self.ed_weight.text()) if self.ed_weight.text() else None,
                material=self.ed_material.text().strip(),
                batch=self.ed_batch.text().strip()
            )
            self.product_instance_dao.insert(entity)

    def load_entity(self):
        """Загружает изделие в форму."""
        if not self.serial_number:
            return

        entity = self.product_instance_dao.get_by_serial(self.serial_number)
        if not entity:
            raise Exception("Изделие не найдено")

        self.ed_serial.setText(str(entity.serial_number))
        
        # Выбор типа
        if entity.id_type:
            for i in range(self.cb_type.count()):
                if self.cb_type.itemData(i) == entity.id_type:
                    self.cb_type.setCurrentIndex(i)
                    break

        # Выбор статуса
        status_map = {"in_assembly": 0, "under_test": 1, "ready": 2}
        if entity.status in status_map:
            self.cb_status.setCurrentIndex(status_map[entity.status])

        # Выбор цеха
        if entity.id_shop:
            for i in range(self.cb_shop.count()):
                if self.cb_shop.itemData(i) == entity.id_shop:
                    self.cb_shop.setCurrentIndex(i)
                    break

        if entity.weight:
            self.ed_weight.setText(str(entity.weight))
        if entity.material:
            self.ed_material.setText(entity.material)
        if entity.batch:
            self.ed_batch.setText(entity.batch)
