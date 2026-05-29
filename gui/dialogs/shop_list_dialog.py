

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

from dao.shop_dao import ShopDAO
from gui.forms.shop_form import ShopForm
from gui.widgets.filtered_table import FilteredTable
from services.report_service import ReportService


class ShopListDialog(QDialog):


    def __init__(self, parent=None):
        super().__init__(parent)
        self.shop_dao = ShopDAO()
        self._setup_ui()
        self._load_shops()

    def _setup_ui(self):
        self.setWindowTitle("Цеха")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout()

        # Таблица
        self.table = FilteredTable()
        self.table.set_headers(["ID", "Название", "Действия"])
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

    def _load_shops(self):
        self.table.clear()
        try:
            shops = self.shop_dao.get_all()
            for s in shops:
                self.table.add_row([s.id_shop, s.name], row_data=s.id_shop)
                pos = self.table.rowCount() - 1

                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(0, 0, 0, 0)

                btn_edit = QPushButton("✏️")
                btn_edit.setToolTip("Редактировать")
                btn_edit.clicked.connect(lambda checked, id=s.id_shop: self._edit_shop(id))
                btn_layout.addWidget(btn_edit)

                btn_del = QPushButton("🗑️")
                btn_del.setToolTip("Удалить")
                btn_del.clicked.connect(lambda checked, id=s.id_shop: self._delete_shop(id))
                btn_layout.addWidget(btn_del)

                btn_widget.setLayout(btn_layout)
                self.table.setCellWidget(pos, 2, btn_widget)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить цеха: {e}")

    def _on_add(self):
        form = ShopForm(parent=self)
        if form.exec_() == ShopForm.Accepted:
            self._load_shops()

    def _on_edit(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите цех для редактирования")
            return

        shop_id = int(self.table.item(self.table.currentRow(), 0).text())
        self._edit_shop(shop_id)

    def _edit_shop(self, shop_id):
        form = ShopForm(shop_id=shop_id, parent=self)
        if form.exec_() == ShopForm.Accepted:
            self._load_shops()

    def _on_delete(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите цех для удаления")
            return

        shop_id = int(self.table.item(self.table.currentRow(), 0).text())
        self._delete_shop(shop_id)

    def _delete_shop(self, shop_id):
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены, что хотите удалить цех ID={shop_id}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                success = self.shop_dao.delete(shop_id)
                if success:
                    self._load_shops()
                    QMessageBox.information(self, "Успех", "Цех удалён")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить цех")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {e}")

    def _on_export(self):
        """Экспортирует данные таблицы в CSV."""
        try:
            data = self.table.get_export_data(["ID", "Название"])
            filename, _ = QFileDialog.getSaveFileName(
                self, "Сохранить CSV", "shops.csv", "CSV (*.csv)"
            )
            if filename:
                ReportService.export_to_csv(data, filename)
                QMessageBox.information(self, "Успех", f"Данные экспортированы в {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать: {e}")

