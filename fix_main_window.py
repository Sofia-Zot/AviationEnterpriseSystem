import codecs

content = '''"""
Главное окно приложения с динамическим меню по роли пользователя (Phase 8).
"""

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QMessageBox,
    QAction,
    QMenuBar,
)
from PyQt5.QtCore import Qt

from models.user import User
from services.role_service import RoleService
from dao.query_dao import QueryDAO
from db.connection import DatabaseConnection
from gui.queries import (
    Query1Window, Query2Window, Query3aWorkersWindow, Query3bEngineersWindow,
    Query4Window, Query5Window, Query6Window, Query7Window,
    Query8Window, Query9Window, Query10Window, Query11Window,
    Query12Window, Query13Window, Query14Window,
)
from gui.dialogs import (
    EmployeeListDialog,
    BrigadeListDialog,
    ProductInstanceListDialog,
    ProductTypeListDialog,
    TechCardListDialog,
    TestListDialog,
)


class MainWindow(QMainWindow):
    """
    Главное окно приложения.
    Меню формируется динамически на основе роли пользователя.
    """

    def __init__(self, user: User, query_dao: QueryDAO = None):
        super().__init__()
        self.user = user
        self.query_dao = query_dao or QueryDAO(DatabaseConnection())
        self.role_service = RoleService()
        self._setup_ui()
        self._create_menu()

    def _setup_ui(self):
        self.setWindowTitle("AviationEnterpriseSystem")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        central_layout = QVBoxLayout()

        welcome_label = QLabel(
            f"<h1>Добро пожаловать, {self.user.login}!</h1>"
            f"<p>Роль: <b>{self.user.role}</b></p>"
            f"<p>ID сотрудника: {self.user.id_employee or '—'}</p>"
        )
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("padding: 50px;")
        central_layout.addWidget(welcome_label)

        accessible_queries = self.role_service.get_accessible_queries(self.user.role)
        info_label = QLabel(
            f"<p>Вам доступны запросы: <b>{accessible_queries}</b></p>"
        )
        info_label.setAlignment(Qt.AlignCenter)
        central_layout.addWidget(info_label)

        central_layout.addStretch()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        self.statusBar().showMessage(
            f"Добро пожаловать, {self.user.login} (роль: {self.user.role})"
        )

    def _create_menu(self):
        menubar = self.menuBar()
        self._create_file_menu(menubar)
        self._create_queries_menu(menubar)
        self._create_edit_menu(menubar)
        self._create_help_menu(menubar)

    def _create_file_menu(self, menubar: QMenuBar):
        file_menu = menubar.addMenu("&Файл")
        exit_action = QAction("В&ыход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _create_queries_menu(self, menubar: QMenuBar):
        queries_menu = menubar.addMenu("&Запросы")
        accessible = self.role_service.get_accessible_queries(self.user.role)

        if not accessible:
            no_access_action = QAction("Нет доступных запросов", self)
            no_access_action.setEnabled(False)
            queries_menu.addAction(no_access_action)
            return

        query_names = {
            1: "Виды изделий по цеху",
            2: "Завершённые изделия",
            3: "Рабочие",
            4: "Участки и начальники",
            5: "Перечень работ",
            6: "Состав бригад",
            7: "Список мастеров",
            8: "Изделия в сборке",
            9: "Бригады для изделия",
            10: "Лаборатории для изделия",
            11: "Прошедшие испытания",
            12: "Испытатели",
            13: "Оборудование для испытаний",
            14: "Сводка по сборке",
        }

        for query_num in range(1, 15):
            if query_num not in accessible:
                continue

            name = query_names.get(query_num, f"Запрос {query_num}")
            action = QAction(f"Запрос {query_num}: {name}", self)
            action.triggered.connect(lambda checked, q=query_num: self.open_query(q))
            queries_menu.addAction(action)

    def _create_edit_menu(self, menubar: QMenuBar):
        edit_menu = menubar.addMenu("&Редактирование")
        role = self.user.role.lower()
        is_admin = role == 'admin'
        is_hr = role in ('admin', 'hr_manager')
        is_technologist = role in ('admin', 'technologist')
        is_tester = role == 'tester'

        # Справочники
        references_menu = edit_menu.addMenu("Справочники")

        if is_hr:
            employees_action = QAction("Сотрудники", self)
            employees_action.triggered.connect(self._open_employee_dialog)
            references_menu.addAction(employees_action)

        if is_hr:
            brigades_action = QAction("Бригады", self)
            brigades_action.triggered.connect(self._open_brigade_dialog)
            references_menu.addAction(brigades_action)

        if is_admin:
            products_action = QAction("Изделия", self)
            products_action.triggered.connect(self._open_product_instance_dialog)
            references_menu.addAction(products_action)

        if is_technologist:
            types_action = QAction("Типы изделий", self)
            types_action.triggered.connect(self._open_product_type_dialog)
            references_menu.addAction(types_action)

        if is_technologist:
            techcards_action = QAction("Технологические карты", self)
            techcards_action.triggered.connect(self._open_tech_card_dialog)
            references_menu.addAction(techcards_action)

        edit_menu.addSeparator()

        # Испытания
        if is_tester or is_admin:
            tests_action = QAction("Испытания", self)
            tests_action.triggered.connect(self._open_test_dialog)
            edit_menu.addAction(tests_action)

    def _create_help_menu(self, menubar: QMenuBar):
        help_menu = menubar.addMenu("Справ&ка")
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def open_query(self, query_number: int):
        query_windows = {
            1: Query1Window,
            2: Query2Window,
            3: Query3aWorkersWindow,
            4: Query4Window,
            5: Query5Window,
            6: Query6Window,
            7: Query7Window,
            8: Query8Window,
            9: Query9Window,
            10: Query10Window,
            11: Query11Window,
            12: Query12Window,
            13: Query13Window,
            14: Query14Window,
        }

        window_class = query_windows.get(query_number)
        if window_class:
            window = window_class(self.query_dao, self)
            window.exec_()
        else:
            QMessageBox.warning(self, "Запрос", f"Запрос {query_number} не реализован")

    # ========== Методы для открытия CRUD-диалогов ==========

    def _open_employee_dialog(self):
        """Открывает диалог сотрудников."""
        dialog = EmployeeListDialog(parent=self)
        dialog.exec_()

    def _open_brigade_dialog(self):
        """Открывает диалог бригад."""
        dialog = BrigadeListDialog(parent=self)
        dialog.exec_()

    def _open_product_instance_dialog(self):
        """Открывает диалог экземпляров изделий."""
        dialog = ProductInstanceListDialog(parent=self)
        dialog.exec_()

    def _open_product_type_dialog(self):
        """Открывает диалог типов изделий."""
        dialog = ProductTypeListDialog(parent=self)
        dialog.exec_()

    def _open_tech_card_dialog(self):
        """Открывает диалог технологических карт."""
        dialog = TechCardListDialog(parent=self)
        dialog.exec_()

    def _open_test_dialog(self):
        """Открывает диалог испытаний."""
        dialog = TestListDialog(parent=self)
        dialog.exec_()

    def _show_about(self):
        QMessageBox.about(
            self,
            "О программе",
            "<h3>AviationEnterpriseSystem</h3>"
            "<p>Система управления авиационным предприятием</p>"
            "<p>Версия 1.0</p>"
            f"<p>Пользователь: <b>{self.user.login}</b></p>"
            f"<p>Роль: <b>{self.user.role}</b></p>",
        )

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите выйти?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
'''

with open('gui/main_window.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('gui/main_window.py written successfully')
