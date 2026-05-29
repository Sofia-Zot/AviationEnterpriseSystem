

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QMessageBox,
    QHeaderView,
    QLabel,
    QWidget,
)
from PyQt5.QtCore import Qt

from dao.tech_card_dao import TechCardDAO
from gui.forms.tech_card_form import TechCardForm


class TechCardListDialog(QDialog):


    def __init__(self, parent=None):
        super().__init__(parent)
        self.tech_card_dao = TechCardDAO()
        self._setup_ui()
        self._load_cards()

    def _setup_ui(self):
        """Настраивает интерфейс."""
        self.setWindowTitle("Технологические карты")
        self.setMinimumSize(800, 500)

        layout = QVBoxLayout()

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Тип изделия", "Действия"])
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

    def _load_cards(self):
        """Загружает технологические карты в таблицу."""
        self.table.setRowCount(0)

        try:
            cards = self.tech_card_dao.get_all_with_relations()
            for card in cards:
                pos = self.table.rowCount()
                self.table.insertRow(pos)

                self.table.setItem(pos, 0, QTableWidgetItem(str(card.id_card)))
                self.table.setItem(pos, 1, QTableWidgetItem(card.product_type_name or "-"))

                # Кнопки действий
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(0, 0, 0, 0)

                btn_edit = QPushButton("✏️")
                btn_edit.setToolTip("Редактировать")
                btn_edit.clicked.connect(lambda checked, id=card.id_card: self._edit_card(id))
                btn_layout.addWidget(btn_edit)

                btn_del = QPushButton("🗑️")
                btn_del.setToolTip("Удалить")
                btn_del.clicked.connect(lambda checked, id=card.id_card: self._delete_card(id))
                btn_layout.addWidget(btn_del)

                btn_widget.setLayout(btn_layout)
                self.table.setCellWidget(pos, 2, btn_widget)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить карты: {e}")

    def _on_cell_double_clicked(self, row, column):
        """Обрабатывает двойной клик по строке таблицы."""
        card_id = int(self.table.item(row, 0).text())
        self._edit_card(card_id)

    def _on_add(self):
        """Открывает форму добавления."""
        form = TechCardForm(parent=self)
        if form.exec_() == TechCardForm.Accepted:
            self._load_cards()

    def _on_edit(self):
        """Открывает форму редактирования."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите карту для редактирования")
            return

        card_id = int(self.table.item(self.table.currentRow(), 0).text())
        self._edit_card(card_id)

    def _edit_card(self, card_id):
        """Открывает форму редактирования."""
        form = TechCardForm(card_id=card_id, parent=self)
        if form.exec_() == TechCardForm.Accepted:
            self._load_cards()

    def _on_delete(self):
        """Удаляет выбранную строку."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите карту для удаления")
            return

        card_id = int(self.table.item(self.table.currentRow(), 0).text())
        self._delete_card(card_id)

    def _delete_card(self, card_id):
        """Удаляет технологическую карту."""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены, что хотите удалить карту ID={card_id}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                success = self.tech_card_dao.delete(card_id)
                if success:
                    self._load_cards()
                    QMessageBox.information(self, "Успех", "Карта удалена")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить (возможно, есть связанные данные)")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {e}")
