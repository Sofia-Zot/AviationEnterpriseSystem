

import logging
import psycopg2
from PyQt5.QtWidgets import (
    QLabel, QLineEdit, QComboBox, QFormLayout, QMessageBox,
    QVBoxLayout, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt

from dao.brigade_dao import BrigadeDAO
from dao.worker_dao import WorkerDAO
from gui.forms.base_form import BaseForm

logger = logging.getLogger(__name__)


class BrigadeForm(BaseForm):

    def __init__(self, brigade_id: int = None, parent=None):
        self.brigade_id = brigade_id
        self.brigade_dao = BrigadeDAO()
        self.worker_dao = WorkerDAO()
        self._entity = None

        super().__init__(parent)
        self.setWindowTitle("Редактирование бригады")
        self.setMinimumWidth(400)

        self._load_sections()
        if self.brigade_id:
            self._load_entity()
        else:
            # Для новой бригады список бригадиров пуст
            self._load_foremen(None)

    def _setup_ui(self):
        """Настраивает интерфейс."""
        layout = QFormLayout()

        self.lbl_name = QLabel("Название *")
        self.lbl_section = QLabel("Участок *")
        self.lbl_foreman = QLabel("Бригадир")

        self.ed_name = QLineEdit()
        self.cb_section = QComboBox()
        self.cb_foreman = QComboBox()

        self.cb_section.currentIndexChanged.connect(self._on_section_changed)

        layout.addRow(self.lbl_name, self.ed_name)
        layout.addRow(self.lbl_section, self.cb_section)
        layout.addRow(self.lbl_foreman, self.cb_foreman)

        # Кнопка снятия бригадира
        self.btn_remove_foreman = QPushButton("Снять бригадира")
        self.btn_remove_foreman.setToolTip("Снять текущего бригадира с должности")
        self.btn_remove_foreman.clicked.connect(self._on_remove_foreman)
        layout.addRow("", self.btn_remove_foreman)

        # Создаём основной layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.btn_save = QPushButton("Сохранить")
        self.btn_save.clicked.connect(self._on_save)
        button_layout.addWidget(self.btn_save)

        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_cancel)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def _load_sections(self):
        """Загружает участки."""
        try:
            from db.connection import DatabaseConnection
            db = DatabaseConnection()
            conn = db.get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT id_section, name FROM section ORDER BY name")
                    for row in cur.fetchall():
                        self.cb_section.addItem(row[1], row[0])
            finally:
                db.return_connection(conn)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить участки: {e}")

    def _load_foremen(self, brigade_id: int = None):
        """
        Загружает рабочих, уже состоящих в данной бригаде.
        Для новой бригады (brigade_id=None) список пуст.
        """
        self.cb_foreman.clear()
        self.cb_foreman.addItem("— не назначен —", None)

        if not brigade_id:
            return

        try:
            from db.connection import DatabaseConnection
            db = DatabaseConnection()
            conn = db.get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT e.id_employee, e.last_name, e.first_name, w.is_foreman
                        FROM worker w
                        JOIN employee e ON w.id_employee = e.id_employee
                        WHERE w.id_brigade = %s
                        ORDER BY e.last_name, e.first_name
                        """,
                        (brigade_id,),
                    )
                    rows = cur.fetchall()
                    for row in rows:
                        foreman_mark = " (бригадир)" if row[3] else ""
                        self.cb_foreman.addItem(
                            f"{row[1]} {row[2]}{foreman_mark}",
                            row[0]
                        )
            finally:
                db.return_connection(conn)
        except Exception as e:
            logger.exception("Ошибка при загрузке бригадиров")
            QMessageBox.critical(self, "Ошибка", "Ошибка при загрузке бригадиров. Подробности в файле app.log")

    def _on_section_changed(self):
        """Обновляет список бригадиров при смене участка."""
        # Список бригадиров привязан к конкретной бригаде, а не к участку
        # При редактировании перезагружаем список для текущей бригады
        if self.brigade_id:
            self._load_foremen(self.brigade_id)
        else:
            # Для новой бригады список всегда пуст
            self._load_foremen(None)

    def validate(self) -> bool:
        """Валидация данных."""
        if not self.ed_name.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название бригады")
            return False
        if not self.cb_section.currentData():
            QMessageBox.warning(self, "Ошибка", "Выберите участок")
            return False
        return True

    def _on_remove_foreman(self):
        """Снимает текущего бригадира."""
        self.cb_foreman.setCurrentIndex(0)  # Устанавливаем "— не назначен —"

    def _get_worker_brigade(self, employee_id: int) -> int:
        """Возвращает id_brigade рабочего или None."""
        worker = self.worker_dao.get_by_id(employee_id)
        if worker:
            return worker.id_brigade
        return None

    def save_entity(self):
        """Сохраняет бригаду."""
        from models.brigade import Brigade
        from db.connection import DatabaseConnection

        new_foreman_id = self.cb_foreman.currentData()

        if self.brigade_id:
            # ===== РЕДАКТИРОВАНИЕ =====
            entity = self.brigade_dao.get_by_id(self.brigade_id)
            if not entity:
                raise Exception("Бригада не найдена")

            old_foreman_id = entity.id_foreman

            # Если назначаем нового бригадира - проверяем, что он в этой бригаде
            if new_foreman_id is not None:
                worker_brigade = self._get_worker_brigade(new_foreman_id)
                if worker_brigade != self.brigade_id:
                    raise Exception(
                        "Выбранный рабочий не состоит в этой бригаде.\n"
                        "Сначала переведите рабочего в эту бригаду через форму сотрудника."
                    )

            # Обновляем бригаду
            entity.name = self.ed_name.text().strip()
            entity.id_section = self.cb_section.currentData()
            entity.id_foreman = new_foreman_id

            db = DatabaseConnection()
            conn = db.get_connection()
            try:
                with conn.cursor() as cur:
                    # Сбрасываем старого бригадира
                    if old_foreman_id and old_foreman_id != new_foreman_id:
                        cur.execute(
                            "UPDATE worker SET is_foreman = FALSE WHERE id_employee = %s",
                            (old_foreman_id,)
                        )

                    # Обновляем бригаду
                    cur.execute(
                        """
                        UPDATE brigade
                        SET name = %s, id_section = %s, id_foreman = %s
                        WHERE id_brigade = %s
                        """,
                        (entity.name, entity.id_section, entity.id_foreman, self.brigade_id)
                    )

                    # Устанавливаем нового бригадира
                    if new_foreman_id:
                        cur.execute(
                            "UPDATE worker SET is_foreman = TRUE WHERE id_employee = %s",
                            (new_foreman_id,)
                        )

                conn.commit()
            except psycopg2.Error as e:
                logger.exception("Ошибка при обновлении бригады")
                if conn:
                    conn.rollback()
                error_msg = str(e)
                if "Foreman must be a worker" in error_msg:
                    raise Exception(
                        "Выбранный рабочий не является членом этой бригады.\n"
                        "Сначала переведите рабочего в эту бригаду через форму сотрудника."
                    )
                elif "Brigade already has a foreman" in error_msg:
                    raise Exception("В бригаде уже есть бригадир. Сначала снимите его.")
                else:
                    raise Exception(f"Ошибка базы данных: {error_msg}")
            finally:
                db.return_connection(conn)
        else:
            # ===== СОЗДАНИЕ =====
            entity = Brigade(
                name=self.ed_name.text().strip(),
                id_section=self.cb_section.currentData(),
                id_foreman=None  # Пока не назначаем - нужен id_brigade
            )

            db = DatabaseConnection()
            conn = db.get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO brigade (name, id_section, id_foreman)
                        VALUES (%s, %s, %s)
                        RETURNING id_brigade
                        """,
                        (entity.name, entity.id_section, None)
                    )
                    row = cur.fetchone()
                    new_brigade_id = row[0]

                    # Если выбран бригадир - проверяем и назначаем
                    if new_foreman_id:
                        # Проверяем, что рабочий существует
                        cur.execute(
                            "SELECT id_brigade FROM worker WHERE id_employee = %s",
                            (new_foreman_id,)
                        )
                        worker_row = cur.fetchone()

                        if not worker_row:
                            conn.rollback()
                            raise Exception("Выбранный сотрудник не является рабочим.")

                        # Обновляем рабочего
                        cur.execute(
                            """
                            UPDATE worker
                            SET is_foreman = TRUE, id_brigade = %s
                            WHERE id_employee = %s
                            """,
                            (new_brigade_id, new_foreman_id)
                        )

                        # Обновляем бригаду
                        cur.execute(
                            "UPDATE brigade SET id_foreman = %s WHERE id_brigade = %s",
                            (new_foreman_id, new_brigade_id)
                        )

                conn.commit()
                self.brigade_id = new_brigade_id
            except psycopg2.Error as e:
                logger.exception("Ошибка при создании бригады")
                if conn:
                    conn.rollback()
                error_msg = str(e)
                if "Foreman must be a worker" in error_msg:
                    raise Exception(
                        "Выбранный рабочий не является членом этой бригады."
                    )
                elif "Brigade already has a foreman" in error_msg:
                    raise Exception("В бригаде уже есть бригадир. Сначала снимите его.")
                else:
                    raise Exception(f"Ошибка базы данных: {error_msg}")
            finally:
                db.return_connection(conn)

    def load_entity(self):
        """Загружает бригаду в форму."""
        if not self.brigade_id:
            return

        entity = self.brigade_dao.get_by_id(self.brigade_id)
        if not entity:
            raise Exception("Бригада не найдена")

        self.ed_name.setText(entity.name or "")
        if entity.id_section:
            for i in range(self.cb_section.count()):
                if self.cb_section.itemData(i) == entity.id_section:
                    self.cb_section.setCurrentIndex(i)
                    break

        # Загружаем список бригадиров для этой бригады
        self._load_foremen(self.brigade_id)

        if entity.id_foreman:
            for i in range(self.cb_foreman.count()):
                if self.cb_foreman.itemData(i) == entity.id_foreman:
                    self.cb_foreman.setCurrentIndex(i)
                    break
