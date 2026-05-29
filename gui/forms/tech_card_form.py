
import logging
from PyQt5.QtWidgets import (
    QLabel, QComboBox, QFormLayout, QMessageBox,
    QListWidget, QListWidgetItem, QPushButton, QHBoxLayout, QVBoxLayout, QGroupBox, QInputDialog
)
from PyQt5.QtCore import Qt

from dao.tech_card_dao import TechCardDAO
from gui.forms.base_form import BaseForm

logger = logging.getLogger(__name__)


class TechCardForm(BaseForm):


    def __init__(self, card_id: int = None, parent=None):
        self.card_id = card_id
        self.tech_card_dao = TechCardDAO()
        self._entity = None
        self._steps = []

        super().__init__(parent)
        self.setWindowTitle("Редактирование технологической карты")
        self.setMinimumWidth(600)

        if self.card_id:
            self._load_entity()

    def _setup_ui(self):
        """Настраивает интерфейс."""
        layout = QVBoxLayout()

        # Основные поля
        form_layout = QFormLayout()

        self.lbl_type = QLabel("Тип изделия *")
        self.cb_type = QComboBox()
        self._load_product_types()

        form_layout.addRow(self.lbl_type, self.cb_type)
        layout.addLayout(form_layout)

        # Этапы работ
        steps_group = QGroupBox("Этапы работ")
        steps_layout = QVBoxLayout()

        self.list_steps = QListWidget()

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Добавить этап")
        btn_add.clicked.connect(self._add_step)
        btn_layout.addWidget(btn_add)

        btn_remove = QPushButton("Удалить этап")
        btn_remove.clicked.connect(self._remove_step)
        btn_layout.addWidget(btn_remove)

        steps_layout.addWidget(self.list_steps)
        steps_layout.addLayout(btn_layout)
        steps_group.setLayout(steps_layout)
        layout.addWidget(steps_group)

        # Кнопки сохранения/отмены
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self._on_save)
        button_layout.addWidget(btn_save)

        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _load_product_types(self):
        """Загружает типы изделий."""
        try:
            from dao.product_type_dao import ProductTypeDAO
            types = ProductTypeDAO().get_all()
            for t in types:
                self.cb_type.addItem(t.name, t.id_type)
        except Exception as e:
            logger.exception("Ошибка при загрузке типов изделий")
            QMessageBox.critical(self, "Ошибка", "Ошибка при загрузке типов изделий. Подробности в файле app.log")

    def _load_available_works(self):
        """Загружает доступные работы для добавления."""
        try:
            from db.connection import DatabaseConnection
            db = DatabaseConnection()
            conn = db.get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT swl.id_work, s.name as section_name, swl.work_name
                        FROM section_work_list swl
                        JOIN section s ON swl.id_section = s.id_section
                        ORDER BY s.name, swl.work_name
                    """)
                    return cur.fetchall()
            finally:
                db.return_connection(conn)
        except Exception as e:
            logger.exception("Ошибка при загрузке работ")
            QMessageBox.critical(self, "Ошибка", "Ошибка при загрузке работ. Подробности в файле app.log")
            return []

    def _add_step(self):
        """Добавляет этап работы."""
        works = self._load_available_works()
        if not works:
            return

        # Создаём простой диалог для выбора
        from PyQt5.QtWidgets import QInputDialog
        work_names = [f"{w[1]}: {w[2]}" for w in works]
        selected, ok = QInputDialog.getItem(
            self,
            "Выберите работу",
            "Доступные работы:",
            work_names,
            0,
            False
        )

        if ok and selected:
            idx = work_names.index(selected)
            work_id = works[idx][0]
            work_name = works[idx][2]
            section_name = works[idx][1]

            # Проверка на дубликат
            for i in range(self.list_steps.count()):
                item = self.list_steps.item(i)
                if item.data(Qt.UserRole) == work_id:
                    QMessageBox.warning(self, "Ошибка", "Этап уже добавлен")
                    return

            item = QListWidgetItem(f"{section_name}: {work_name}")
            item.setData(Qt.UserRole, work_id)
            self.list_steps.addItem(item)
            self._steps.append({'work_id': work_id, 'section_name': section_name, 'work_name': work_name})

    def _remove_step(self):
        """Удаляет выбранный этап."""
        current = self.list_steps.currentRow()
        if current >= 0:
            self.list_steps.takeItem(current)
            if current < len(self._steps):
                self._steps.pop(current)

    def validate(self) -> bool:
        """Валидация данных."""
        if not self.cb_type.currentData():
            QMessageBox.warning(self, "Ошибка", "Выберите тип изделия")
            return False
        return True

    def save_entity(self):
        """Сохраняет технологическую карту."""
        from models.tech_card import TechCard

        if self.card_id:
            entity = self.tech_card_dao.get_by_id(self.card_id)
            if not entity:
                raise Exception("Техкарта не найдена")
            entity.id_type = self.cb_type.currentData()
            self.tech_card_dao.update(entity)
            # Удаляем старые этапы и добавляем новые
            self.tech_card_dao.delete_steps(self.card_id)
            for step in self._steps:
                self.tech_card_dao.add_step(self.card_id, step['work_id'])
        else:
            entity = TechCard(
                id_type=self.cb_type.currentData()
            )
            self.tech_card_dao.insert(entity)
            self.card_id = entity.id_card
            # Добавляем этапы
            for step in self._steps:
                self.tech_card_dao.add_step(self.card_id, step['work_id'])

    def load_entity(self):
        """Загружает техкарту в форму."""
        if not self.card_id:
            return

        entity = self.tech_card_dao.get_by_id(self.card_id)
        if not entity:
            raise Exception("Техкарта не найдена")

        # Выбор типа
        if entity.id_type:
            for i in range(self.cb_type.count()):
                if self.cb_type.itemData(i) == entity.id_type:
                    self.cb_type.setCurrentIndex(i)
                    break

        # Загрузка этапов
        self.list_steps.clear()
        self._steps = []
        try:
            steps = self.tech_card_dao.get_steps(self.card_id)
            for step in steps:
                item = QListWidgetItem(f"{step['section_name']}: {step['work_name']}")
                item.setData(Qt.UserRole, step['id_work'])
                self.list_steps.addItem(item)
                self._steps.append({
                    'work_id': step['id_work'],
                    'section_name': step['section_name'],
                    'work_name': step['work_name'],
                })
        except Exception as e:
            logger.exception("Ошибка при загрузке этапов")
            QMessageBox.critical(self, "Ошибка", "Ошибка при загрузке этапов. Подробности в файле app.log")
