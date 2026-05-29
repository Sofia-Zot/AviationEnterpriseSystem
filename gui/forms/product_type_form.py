
import logging
from PyQt5.QtWidgets import (
    QLabel, QLineEdit, QComboBox, QFormLayout, QMessageBox,
    QVBoxLayout, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt

from dao.product_type_dao import ProductTypeDAO
from gui.forms.base_form import BaseForm

logger = logging.getLogger(__name__)


class ProductTypeForm(BaseForm):


    def __init__(self, type_id: int = None, parent=None):
        self.type_id = type_id
        self.product_type_dao = ProductTypeDAO()
        self._entity = None

        super().__init__(parent)
        self.setWindowTitle("Редактирование типа изделия")
        self.setMinimumWidth(400)

        if self.type_id:
            self._load_entity()

    def _setup_ui(self):
        """Настраивает интерфейс."""
        layout = QFormLayout()

        self.lbl_name = QLabel("Название *")
        self.lbl_category = QLabel("Категория *")

        self.ed_name = QLineEdit()

        self.cb_category = QComboBox()
        self._load_categories()

        layout.addRow(self.lbl_name, self.ed_name)
        layout.addRow(self.lbl_category, self.cb_category)

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

    def _load_categories(self):
        """Загружает категории."""
        try:
            from db.connection import DatabaseConnection
            db = DatabaseConnection()
            conn = db.get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT id_category, name FROM product_category ORDER BY name")
                    for row in cur.fetchall():
                        self.cb_category.addItem(row[1], row[0])
            finally:
                db.return_connection(conn)
        except Exception as e:
            logger.exception("Ошибка при загрузке категорий")
            QMessageBox.critical(self, "Ошибка", "Ошибка при загрузке категорий. Подробности в файле app.log")

    def validate(self) -> bool:
        """Валидация данных."""
        if not self.ed_name.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название типа")
            return False
        if not self.cb_category.currentData():
            QMessageBox.warning(self, "Ошибка", "Выберите категорию")
            return False
        return True

    def save_entity(self):
        """Сохраняет тип изделия."""
        from models.product_type import ProductType

        if self.type_id:
            entity = self.product_type_dao.get_by_id(self.type_id)
            if not entity:
                raise Exception("Тип изделия не найден")
            entity.name = self.ed_name.text().strip()
            entity.id_category = self.cb_category.currentData()
            self.product_type_dao.update(entity)
        else:
            entity = ProductType(
                name=self.ed_name.text().strip(),
                id_category=self.cb_category.currentData(),
            )
            self.product_type_dao.insert(entity)

    def load_entity(self):
        """Загружает тип изделия в форму."""
        if not self.type_id:
            return

        entity = self.product_type_dao.get_by_id(self.type_id)
        if not entity:
            raise Exception("Тип изделия не найден")

        self.ed_name.setText(entity.name or "")

        # Выбор категории
        if entity.id_category:
            for i in range(self.cb_category.count()):
                if self.cb_category.itemData(i) == entity.id_category:
                    self.cb_category.setCurrentIndex(i)
                    break

