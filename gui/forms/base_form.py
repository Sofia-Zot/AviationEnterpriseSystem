

import logging
from abc import abstractmethod

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
)

logger = logging.getLogger(__name__)


class BaseForm(QDialog):


    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Настраивает базовый интерфейс."""
        layout = QVBoxLayout()

        # Поля ввода добавляются в наследниках
        self.form_layout = QVBoxLayout()
        layout.addLayout(self.form_layout)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.btn_save = QPushButton("Сохранить")
        self.btn_save.clicked.connect(self._on_save)
        button_layout.addWidget(self.btn_save)

        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_cancel)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    @abstractmethod
    def validate(self) -> bool:
        """
        Валидация данных формы.
        Возвращает True, если данные валидны.
        """
        pass

    @abstractmethod
    def save_entity(self):
        """Сохраняет сущность в БД."""
        pass

    @abstractmethod
    def load_entity(self):
        """Загружает сущность в форму."""
        pass

    def _load_entity(self):
        """Внутренний хелпер для вызова load_entity."""
        self.load_entity()

    def _on_save(self):
        """Обработчик кнопки 'Сохранить'."""
        if not self.validate():
            QMessageBox.warning(self, "Валидация", "Проверьте введенные данные")
            return

        try:
            self.save_entity()
            self.accept()
        except Exception as e:
            logger.exception("Ошибка при сохранении сущности")
            QMessageBox.critical(self, "Ошибка", f"{e}\n\nПодробности в файле app.log")
