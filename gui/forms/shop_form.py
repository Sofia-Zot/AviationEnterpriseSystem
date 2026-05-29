

from PyQt5.QtWidgets import QLabel, QLineEdit, QFormLayout, QMessageBox

from dao.shop_dao import ShopDAO
from gui.forms.base_form import BaseForm
from models.shop import Shop


class ShopForm(BaseForm):


    def __init__(self, shop_id: int = None, parent=None):
        self.shop_id = shop_id
        self.shop_dao = ShopDAO()

        super().__init__(parent)
        self.setWindowTitle("Редактирование цеха")
        self.setMinimumWidth(400)

        if self.shop_id:
            self.load_entity()

    def _setup_ui(self):
        layout = QFormLayout()

        self.lbl_name = QLabel("Название *")
        self.ed_name = QLineEdit()

        layout.addRow(self.lbl_name, self.ed_name)
        self.form_layout.addLayout(layout)

    def validate(self) -> bool:
        if not self.ed_name.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название цеха")
            return False
        return True

    def save_entity(self):
        if self.shop_id:
            entity = self.shop_dao.get_by_id(self.shop_id)
            if not entity:
                raise Exception("Цех не найден")
            entity.name = self.ed_name.text().strip()
            self.shop_dao.update(entity)
        else:
            entity = Shop(name=self.ed_name.text().strip())
            self.shop_dao.insert(entity)

    def load_entity(self):
        if not self.shop_id:
            return

        entity = self.shop_dao.get_by_id(self.shop_id)
        if not entity:
            raise Exception("Цех не найден")

        self.ed_name.setText(entity.name or "")
