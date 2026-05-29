

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtCore import Qt

from services.auth_service import AuthService
from models.user import User


class LoginWindow(QDialog):


    def __init__(self, auth_service: AuthService, parent=None):
        """
        Args:
            auth_service: Экземпляр AuthService для аутентификации.
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self.auth_service = auth_service
        self.user = None
        self._setup_ui()
        self.setMinimumWidth(350)

    def _setup_ui(self):
        """Настраивает элементы интерфейса."""
        self.setWindowTitle("Авторизация — AviationEnterpriseSystem")
        self.setModal(True)

        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("AviationEnterpriseSystem")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(10)

        # Логин
        login_layout = QHBoxLayout()
        login_layout.addWidget(QLabel("Логин:"))
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        self.login_input.returnPressed.connect(self._on_login)
        login_layout.addWidget(self.login_input)
        layout.addLayout(login_layout)

        # Пароль
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Пароль:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self._on_login)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        layout.addSpacing(15)

        # Кнопки
        button_layout = QHBoxLayout()

        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_cancel)

        button_layout.addStretch()

        self.btn_login = QPushButton("Вход")
        self.btn_login.setDefault(True)
        self.btn_login.clicked.connect(self._on_login)
        button_layout.addWidget(self.btn_login)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _on_login(self):
        """Обработчик нажатия кнопки 'Вход'."""
        login = self.login_input.text().strip()
        password = self.password_input.text()

        if not login:
            QMessageBox.warning(self, "Ошибка", "Введите логин")
            self.login_input.setFocus()
            return

        if not password:
            QMessageBox.warning(self, "Ошибка", "Введите пароль")
            self.password_input.setFocus()
            return

        try:
            user = self.auth_service.authenticate(login, password)
            if user is not None:
                self.user = user
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    "Ошибка авторизации",
                    "Неверный логин или пароль",
                )
                self.password_input.clear()
                self.password_input.setFocus()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Ошибка при авторизации:\n{str(e)}",
            )

    def get_user(self) -> User:
        """
        Возвращает авторизованного пользователя.

        Returns:
            User: Объект пользователя или None.
        """
        return self.user
