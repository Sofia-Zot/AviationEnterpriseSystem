

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QHeaderView,
    QWidget,
    QComboBox,
    QLabel,
    QAbstractItemView,
    QFileDialog,
)
from PyQt5.QtCore import Qt

from dao.section_dao import SectionDAO
from dao.shop_dao import ShopDAO
from gui.forms.section_form import SectionForm
from gui.widgets.filtered_table import FilteredTable
from services.report_service import ReportService


class SectionListDialog(QDialog):


    def __init__(self, parent=None):
        super().__init__(parent)
        self.section_dao = SectionDAO()
        self.shop_dao = ShopDAO()
        self._setup_ui()
        self._load_sections()

    def _setup_ui(self):
        self.setWindowTitle("Участки")
        self.setMinimumSize(700, 450)

        layout = QVBoxLayout()

        # Фильтр по цеху
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Цех:"))

        self.cb_shop_filter = QComboBox()
        self.cb_shop_filter.addItem("Все цеха", "all")
        self._load_shops()
        self.cb_shop_filter.currentIndexChanged.connect(self._on_filter)
        filter_layout.addWidget(self.cb_shop_filter)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Таблица
        self.table = FilteredTable()
        self.table.set_headers(["ID", "Название", "Цех", "Действия"])
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
        try:
            shops = self.shop_dao.get_all()
            for s in shops:
                self.cb_shop_filter.addItem(s.name, s.id_shop)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить цеха: {e}")

    def _load_sections(self):
        self.table.clear()
        try:
            sections = self.section_dao.get_all()
            for s in sections:
                shop_name = self._get_shop_name(s.id_shop)
                self.table.add_row([s.id_section, s.name, shop_name], row_data=s.id_section)
                pos = self.table.rowCount() - 1

                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(0, 0, 0, 0)

                btn_edit = QPushButton("✏️")
                btn_edit.setToolTip("Редактировать")
                btn_edit.clicked.connect(lambda checked, id=s.id_section: self._edit_section(id))
                btn_layout.addWidget(btn_edit)

                btn_del = QPushButton("🗑️")
                btn_del.setToolTip("Удалить")
                btn_del.clicked.connect(lambda checked, id=s.id_section: self._delete_section(id))
                btn_layout.addWidget(btn_del)

                btn_widget.setLayout(btn_layout)
                self.table.setCellWidget(pos, 3, btn_widget)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить участки: {e}")

    def _get_shop_name(self, shop_id):
        shop = self.shop_dao.get_by_id(shop_id)
        return shop.name if shop else "-"

    def _on_filter(self, index):
        shop_id = self.cb_shop_filter.currentData()
        current_shop_name = self.cb_shop_filter.currentText()

        for row in range(self.table.rowCount()):
            if shop_id == "all":
                self.table.setRowHidden(row, False)
            else:
                item = self.table.item(row, 2)
                shop_name = item.text() if item else ""
                self.table.setRowHidden(row, shop_name != current_shop_name)

    def _on_add(self):
        form = SectionForm(parent=self)
        if form.exec_() == SectionForm.Accepted:
            self._load_sections()

    def _on_edit(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите участок для редактирования")
            return

        section_id = int(self.table.item(self.table.currentRow(), 0).text())
        self._edit_section(section_id)

    def _edit_section(self, section_id):
        form = SectionForm(section_id=section_id, parent=self)
        if form.exec_() == SectionForm.Accepted:
            self._load_sections()

    def _on_delete(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите участок для удаления")
            return

        section_id = int(self.table.item(self.table.currentRow(), 0).text())
        self._delete_section(section_id)

    def _delete_section(self, section_id):
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены, что хотите удалить участок ID={section_id}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                success = self.section_dao.delete(section_id)
                if success:
                    self._load_sections()
                    QMessageBox.information(self, "Успех", "Участок удалён")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить участок")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {e}")

    def _on_export(self):
        """Экспортирует данные таблицы в CSV."""
        try:
            data = self.table.get_export_data(["ID", "Название", "Цех"])
            filename, _ = QFileDialog.getSaveFileName(
                self, "Сохранить CSV", "sections.csv", "CSV (*.csv)"
            )
            if filename:
                ReportService.export_to_csv(data, filename)
                QMessageBox.information(self, "Успех", f"Данные экспортированы в {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать: {e}")

