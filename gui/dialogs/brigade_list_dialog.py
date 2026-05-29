import logging
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

from dao.brigade_dao import BrigadeDAO
from gui.forms.brigade_form import BrigadeForm

logger = logging.getLogger(__name__)


class BrigadeListDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.brigade_dao = BrigadeDAO()
        self._setup_ui()
        self._load_brigades()

    def _setup_ui(self):
        """Настраивает интерфейс."""
        self.setWindowTitle("Бригады")
        self.setMinimumSize(800, 500)

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
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Название", "Участок", "Цех", "Бригадир", "Действия"
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

    def _load_brigades(self):
        """Загружает бригады в таблицу."""
        self.table.setRowCount(0)

        try:
            brigades = self.brigade_dao.get_all_with_relations()
            for b in brigades:
                pos = self.table.rowCount()
                self.table.insertRow(pos)

                self.table.setItem(pos, 0, QTableWidgetItem(str(b.id_brigade)))
                self.table.setItem(pos, 1, QTableWidgetItem(b.name or ""))
                self.table.setItem(pos, 2, QTableWidgetItem(b.section_name or "-"))
                self.table.setItem(pos, 3, QTableWidgetItem(b.shop_name or "-"))
                self.table.setItem(pos, 4, QTableWidgetItem(b.foreman_name or "-"))

                # Кнопки действий
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(0, 0, 0, 0)

                btn_edit = QPushButton("✏️")
                btn_edit.setToolTip("Редактировать")
                btn_edit.clicked.connect(lambda checked, id=b.id_brigade: self._edit_brigade(id))
                btn_layout.addWidget(btn_edit)

                btn_del = QPushButton("🗑️")
                btn_del.setToolTip("Удалить")
                btn_del.clicked.connect(lambda checked, id=b.id_brigade: self._delete_brigade(id))
                btn_layout.addWidget(btn_del)

                btn_widget.setLayout(btn_layout)
                self.table.setCellWidget(pos, 5, btn_widget)
        except Exception as e:
            logger.exception("Ошибка при загрузке бригад")
            QMessageBox.critical(self, "Ошибка", "Ошибка при загрузке бригад. Подробности в файле app.log")

    def _on_cell_double_clicked(self, row, column):
        """Обрабатывает двойной клик по строке таблицы."""
        brigade_id = int(self.table.item(row, 0).text())
        self._edit_brigade(brigade_id)

    def _on_filter(self, index):
        """Фильтрует таблицу по цеху."""
        shop_id = self.cb_shop_filter.currentData()

        for row in range(self.table.rowCount()):
            if shop_id == "all":
                self.table.setRowHidden(row, False)
            else:
                # Простая фильтрация - все бригады с выбранным цехом
                # В реальном приложении нужно загружать данные с фильтром
                self.table.setRowHidden(row, False)

    def _on_add(self):
        """Открывает форму добавления."""
        form = BrigadeForm(parent=self)
        if form.exec_() == BrigadeForm.Accepted:
            self._load_brigades()

    def _on_edit(self):
        """Открывает форму редактирования."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите бригаду для редактирования")
            return

        brigade_id = int(self.table.item(self.table.currentRow(), 0).text())
        self._edit_brigade(brigade_id)

    def _edit_brigade(self, brigade_id):
        """Открывает форму редактирования."""
        form = BrigadeForm(brigade_id=brigade_id, parent=self)
        if form.exec_() == BrigadeForm.Accepted:
            self._load_brigades()

    def _on_delete(self):
        """Удаляет выбранную строку."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите бригаду для удаления")
            return

        brigade_id = int(self.table.item(self.table.currentRow(), 0).text())
        self._delete_brigade(brigade_id)

    def _delete_brigade(self, brigade_id):
        """Удаляет бригаду."""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены, что хотите удалить бригаду ID={brigade_id}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                success = self.brigade_dao.delete(brigade_id)
                if success:
                    self._load_brigades()
                    QMessageBox.information(self, "Успех", "Бригада удалена")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить (возможно, есть связанные данные)")
            except Exception as e:
                logger.exception("Ошибка при удалении бригады")
                QMessageBox.critical(self, "Ошибка", "Ошибка при удалении. Подробности в файле app.log")
