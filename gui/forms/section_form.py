

from PyQt5.QtWidgets import QLabel, QLineEdit, QComboBox, QFormLayout, QMessageBox

from dao.section_dao import SectionDAO
from dao.shop_dao import ShopDAO
from gui.forms.base_form import BaseForm
from models.section import Section


class SectionForm(BaseForm):


    def __init__(self, section_id: int = None, parent=None):
        self.section_id = section_id
        self.section_dao = SectionDAO()
        self.shop_dao = ShopDAO()

        super().__init__(parent)
        self.setWindowTitle("Редактирование участка")
        self.setMinimumWidth(400)

        if self.section_id:
            self.load_entity()

    def _setup_ui(self):
        layout = QFormLayout()

        self.lbl_name = QLabel("Название *")
        self.ed_name = QLineEdit()

        self.lbl_shop = QLabel("Цех *")
        self.cb_shop = QComboBox()
        self._load_shops()

        layout.addRow(self.lbl_name, self.ed_name)
        layout.addRow(self.lbl_shop, self.cb_shop)
        self.form_layout.addLayout(layout)

    def _load_shops(self):
        self.cb_shop.clear()
        try:
            shops = self.shop_dao.get_all()
            for s in shops:
                self.cb_shop.addItem(s.name, s.id_shop)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить цеха: {e}")

    def validate(self) -> bool:
        if not self.ed_name.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название участка")
            return False
        if not self.cb_shop.currentData():
            QMessageBox.warning(self, "Ошибка", "Выберите цех")
            return False
        return True

    def save_entity(self):
        if self.section_id:
            entity = self.section_dao.get_by_id(self.section_id)
            if not entity:
                raise Exception("Участок не найден")
            entity.name = self.ed_name.text().strip()
            entity.id_shop = self.cb_shop.currentData()
            self.section_dao.update(entity)
        else:
            entity = Section(
                name=self.ed_name.text().strip(),
                id_shop=self.cb_shop.currentData(),
            )
            self.section_dao.insert(entity)

    def load_entity(self):
        if not self.section_id:
            return

        entity = self.section_dao.get_by_id(self.section_id)
        if not entity:
            raise Exception("Участок не найден")

        self.ed_name.setText(entity.name or "")
        if entity.id_shop:
            for i in range(self.cb_shop.count()):
                if self.cb_shop.itemData(i) == entity.id_shop:
                    self.cb_shop.setCurrentIndex(i)
                    break
