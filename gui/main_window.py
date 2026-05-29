

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
            f"<h1>Welcome {self.user.login}!</h1>"
            f"<p>Role: <b>{self.user.role}</b></p>"
            f"<p>Employee ID: {self.user.id_employee or 'N/A'}</p>"
        )
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("padding: 50px;")
        central_layout.addWidget(welcome_label)

        accessible_queries = self.role_service.get_accessible_queries(self.user.role)
        info_label = QLabel(
            f"<p>Available queries: <b>{accessible_queries}</b></p>"
        )
        info_label.setAlignment(Qt.AlignCenter)
        central_layout.addWidget(info_label)

        central_layout.addStretch()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        self.statusBar().showMessage(
            f"Welcome {self.user.login} (role: {self.user.role})"
        )

    def _create_menu(self):
        menubar = self.menuBar()
        self._create_file_menu(menubar)
        self._create_queries_menu(menubar)
        self._create_edit_menu(menubar)
        self._create_help_menu(menubar)

    def _create_file_menu(self, menubar: QMenuBar):
        file_menu = menubar.addMenu("&File")
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _create_queries_menu(self, menubar: QMenuBar):
        queries_menu = menubar.addMenu("&Queries")
        accessible = self.role_service.get_accessible_queries(self.user.role)

        if not accessible:
            no_access_action = QAction("No available queries", self)
            no_access_action.setEnabled(False)
            queries_menu.addAction(no_access_action)
            return

        query_names = {
            1: "Product types by shop",
            2: "Completed products",
            3: "Staff",
            4: "Sections and managers",
            5: "Work steps",
            6: "Brigade members",
            7: "Masters",
            8: "Products in assembly",
            9: "Brigades for product",
            10: "Labs for product",
            11: "Tested products",
            12: "Testers",
            13: "Equipment for tests",
            14: "Assembly summary",
        }

        for query_num in range(1, 15):
            if query_num not in accessible:
                continue

            name = query_names.get(query_num, f"Query {query_num}")
            action = QAction(f"Query {query_num}: {name}", self)
            action.triggered.connect(lambda checked, q=query_num: self.open_query(q))
            queries_menu.addAction(action)

    def _create_edit_menu(self, menubar: QMenuBar):
        edit_menu = menubar.addMenu("&Edit")
        role = self.user.role.lower()
        is_admin = role == 'admin'
        is_hr = role in ('admin', 'hr_manager')
        is_technologist = role in ('admin', 'technologist')
        is_tester = role == 'tester'

        references_menu = edit_menu.addMenu("References")

        if is_hr:
            employees_action = QAction("Employees", self)
            employees_action.triggered.connect(self._open_employee_dialog)
            references_menu.addAction(employees_action)

        if is_hr:
            brigades_action = QAction("Brigades", self)
            brigades_action.triggered.connect(self._open_brigade_dialog)
            references_menu.addAction(brigades_action)

        if is_admin:
            products_action = QAction("Products", self)
            products_action.triggered.connect(self._open_product_instance_dialog)
            references_menu.addAction(products_action)

        if is_technologist:
            types_action = QAction("Product Types", self)
            types_action.triggered.connect(self._open_product_type_dialog)
            references_menu.addAction(types_action)

        if is_technologist:
            techcards_action = QAction("Tech Cards", self)
            techcards_action.triggered.connect(self._open_tech_card_dialog)
            references_menu.addAction(techcards_action)

        edit_menu.addSeparator()

        if is_tester or is_admin:
            tests_action = QAction("Tests", self)
            tests_action.triggered.connect(self._open_test_dialog)
            edit_menu.addAction(tests_action)

    def _create_help_menu(self, menubar: QMenuBar):
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
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
            QMessageBox.warning(self, "Error", f"Query {query_number} not available")

    def _open_employee_dialog(self):
        dialog = EmployeeListDialog(parent=self)
        dialog.exec_()

    def _open_brigade_dialog(self):
        dialog = BrigadeListDialog(parent=self)
        dialog.exec_()

    def _open_product_instance_dialog(self):
        dialog = ProductInstanceListDialog(parent=self)
        dialog.exec_()

    def _open_product_type_dialog(self):
        dialog = ProductTypeListDialog(parent=self)
        dialog.exec_()

    def _open_tech_card_dialog(self):
        dialog = TechCardListDialog(parent=self)
        dialog.exec_()

    def _open_test_dialog(self):
        dialog = TestListDialog(parent=self)
        dialog.exec_()

    def _show_about(self):
        QMessageBox.about(
            self,
            "About",
            "<h3>AviationEnterpriseSystem</h3>"
            "<p>Aircraft manufacturing enterprise system</p>"
            "<p>Version 1.0</p>"
            f"<p>User: <b>{self.user.login}</b></p>"
            f"<p>Role: <b>{self.user.role}</b></p>",
        )

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Confirm",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
