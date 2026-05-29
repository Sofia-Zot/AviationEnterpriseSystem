"""
Создаёт view_testers для запроса 12.
Запустить один раз: python scripts/create_view_testers.py
"""

import psycopg2
import configparser

config = configparser.ConfigParser()
config.read('db/config.ini', encoding='utf-8')

conn = psycopg2.connect(
    host=config.get('database', 'host'),
    database=config.get('database', 'dbname'),
    user=config.get('database', 'user'),
    password=config.get('database', 'password'),
    port=config.getint('database', 'port')
)

cur = conn.cursor()

sql = """
DROP VIEW IF EXISTS view_testers CASCADE;
CREATE VIEW view_testers AS
SELECT DISTINCT
    e.id_employee AS id_tester,
    e.last_name,
    e.first_name,
    e.middle_name,
    t.specialization,
    eq.id_lab,
    lab.name AS lab_name,
    pi.serial_number,
    pt.id_category,
    pc.name AS category_name,
    te.end_date AS test_date
FROM employee e
JOIN tester t ON e.id_employee = t.id_employee
JOIN tester_equipment teq ON t.id_employee = teq.id_tester
JOIN equipment eq ON teq.id_equipment = eq.id_equipment
JOIN laboratory lab ON eq.id_lab = lab.id_lab
JOIN test_work_list twl ON eq.id_equipment = twl.id_equipment
JOIN test_step ts ON twl.id_test_work = ts.id_test_work
JOIN test_execution te ON ts.id_step = te.id_test_step
JOIN product_instance pi ON te.serial_number = pi.serial_number
JOIN product_type pt ON pi.id_type = pt.id_type
JOIN product_category pc ON pt.id_category = pc.id_category;
"""

cur.execute(sql)
conn.commit()
print("OK: view_testers created successfully")
cur.close()
conn.close()
