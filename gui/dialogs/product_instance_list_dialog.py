
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QMessageBox,
    QHeaderView,
    QComboBox,
    QLabel,
    QWidget,
)
from PyQt5.QtCore import Qt

from dao.product_instance_dao import ProductInstanceDAO
from gui.forms.product_instance_form import ProductInstanceForm


class ProductInstanceListDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.product_instance_dao = ProductInstanceDAO()
        self._setup_ui()
        self._load_instances()

    def _setup_ui(self):
        """Настраивает интерфейс."""
        self.setWindowTitle("Экземпляры изделий")
        self.setMinimumSize(900, 500)

        layout = QVBoxLayout()

        # Фильтры
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Цех:"))

        self.cb_shop_filter = QComboBox()
        self.cb_shop_filter.addItem("Все цеха", "all")
        self._load_shops()
        self.cb_shop_filter.currentIndexChanged.connect(self._on_filter)
        filter_layout.addWidget(self.cb_shop_filter)

        filter_layout.addWidget(QLabel("Статус:"))
        self.cb_status_filter = QComboBox()
        self.cb_status_filter.addItem("Все", "all")
        self.cb_status_filter.addItem("В сборке", "in_assembly")
        self.cb_status_filter.addItem("На испытаниях", "under_test")
        self.cb_status_filter.addItem("Готово", "ready")
        self.cb_status_filter.currentIndexChanged.connect(self._on_filter)
        filter_layout.addWidget(self.cb_status_filter)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Серийный №", "Тип изделия", "Статус", "Цех", "Вес", "Действия"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)
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

        self.btn_close = QPushButton("Закрыть")
        self.btn_close.clicked.connect(self.close)
        button_layout.addWidget(self.btn_close)

        layout.addLayout(button_layout)

        self.setLayout(layout)

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
                        self.cb_shop_filter.addItem(row[1], row[0])
            finally:
                db.return_connection(conn)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить цеха: {e}")

    def _load_instances(self):
        """Загружает экземпляры изделий в таблицу."""
        self.table.setRowCount(0)

        try:
            instances = self.product_instance_dao.get_all_with_relations()
            for inst in instances:
                pos = self.table.rowCount()
                self.table.insertRow(pos)

                self.table.setItem(pos, 0, QTableWidgetItem(str(inst.serial_number)))
                self.table.setItem(pos, 1, QTableWidgetItem(inst.product_type_name or "-"))
                self.table.setItem(pos, 2, QTableWidgetItem(self._format_status(inst.status)))
                self.table.setItem(pos, 3, QTableWidgetItem(inst.shop_name or "-"))
                self.table.setItem(pos, 4, QTableWidgetItem(str(inst.weight or "-")))

                # Кнопки действий
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(0, 0, 0, 0)

                btn_edit = QPushButton("✏️")
                btn_edit.setToolTip("Редактировать")
                btn_edit.clicked.connect(lambda checked, sn=inst.serial_number: self._edit_instance(sn))
                btn_layout.addWidget(btn_edit)

                btn_del = QPushButton("🗑️")
                btn_del.setToolTip("Удалить")
                btn_del.clicked.connect(lambda checked, sn=inst.serial_number: self._delete_instance(sn))
                btn_layout.addWidget(btn_del)

                btn_widget.setLayout(btn_layout)
                self.table.setCellWidget(pos, 5, btn_widget)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить изделия: {e}")

    def _format_status(self, status):
        """Форматирует статус."""
        statuses = {
            'in_assembly': 'В сборке',
            'under_test': 'На испытаниях',
            'ready': 'Готово',
        }
        return statuses.get(status, status)

    def _on_filter(self, index):
        """Фильтрует таблицу."""
        shop_id = self.cb_shop_filter.currentData()
        status = self.cb_status_filter.currentData()

        for row in range(self.table.rowCount()):
            shop_item = self.table.item(row, 3)
            status_item = self.table.item(row, 2)

            shop_match = shop_id == "all" or (shop_item and str(shop_id) in str(shop_item.text()))
            status_match = status == "all" or (status_item and status_item.text() == self._format_status(status))

            self.table.setRowHidden(row, not (shop_match and status_match))

    def _on_cell_double_clicked(self, row, column):
        """Обрабатывает двойной клик по строке таблицы."""
        serial = int(self.table.item(row, 0).text())
        self._edit_instance(serial)

    def _on_add(self):
        """Открывает форму добавления."""
        form = ProductInstanceForm(parent=self)
        if form.exec_() == ProductInstanceForm.Accepted:
            self._load_instances()

    def _on_edit(self):
        """Открывает форму редактирования."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите изделие для редактирования")
            return

        serial = int(self.table.item(self.table.currentRow(), 0).text())
        self._edit_instance(serial)

    def _edit_instance(self, serial_number):
        """Открывает форму редактирования."""
        form = ProductInstanceForm(serial_number=serial_number, parent=self)
        if form.exec_() == ProductInstanceForm.Accepted:
            self._load_instances()

    def _on_delete(self):
        """Удаляет выбранную строку."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите изделие для удаления")
            return

        serial = int(self.table.item(self.table.currentRow(), 0).text())
        self._delete_instance(serial)

    def _delete_instance(self, serial_number):
        """Удаляет экземпляр изделия."""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены, что хотите удалить изделие с серийным номером {serial_number}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                success = self.product_instance_dao.delete(serial_number)
                if success:
                    self._load_instances()
                    QMessageBox.information(self, "Успех", "Изделие удалено")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить (возможно, есть связанные данные)")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {e}")
