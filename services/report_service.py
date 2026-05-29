
import csv
import os
from datetime import datetime


class ReportService:


    @staticmethod
    def export_to_csv(data, filename):
        """
        Экспортирует данные в CSV-файл.

        Args:
            data: Список словарей или список списков.
            filename: Путь к выходному файлу (без расширения или с .csv).

        Returns:
            str: Полный путь к сохранённому файлу.
        """
        if not data:
            raise ValueError("Нет данных для экспорта")

        if not filename.endswith(".csv"):
            filename += ".csv"

        keys = data[0].keys() if isinstance(data[0], dict) else None

        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            if keys:
                writer = csv.DictWriter(f, fieldnames=keys, delimiter=";")
                writer.writeheader()
                writer.writerows(data)
            else:
                writer = csv.writer(f, delimiter=";")
                for row in data:
                    writer.writerow(row)

        return os.path.abspath(filename)

    @staticmethod
    def table_to_dicts(table_widget, columns):
        """
        Преобразует данные QTableWidget в список словарей для экспорта.

        Args:
            table_widget: Экземпляр QTableWidget (или внутреннюю таблицу FilteredTable).
            columns: Список имён столбцов (ключей словаря).

        Returns:
            list[dict]: Данные таблицы.
        """
        result = []
        for row in range(table_widget.rowCount()):
            if table_widget.isRowHidden(row):
                continue
            row_dict = {}
            for col, key in enumerate(columns):
                item = table_widget.item(row, col)
                row_dict[key] = item.text() if item else ""
            result.append(row_dict)
        return result
