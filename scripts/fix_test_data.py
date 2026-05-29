"""
Добавляет недостающие данные для тестов (запросы 1-14).
Запустить один раз: python scripts/fix_test_data.py
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

print('=== Checking data ===')

# Проверяем, есть ли сотрудники
cur.execute('SELECT COUNT(*) FROM employee')
emp_count = cur.fetchone()[0]
print('employee rows:', emp_count)

# Проверяем, есть ли worker
cur.execute('SELECT COUNT(*) FROM worker')
worker_count = cur.fetchone()[0]
print('worker rows:', worker_count)

# Проверяем, есть ли бригады
cur.execute('SELECT COUNT(*) FROM brigade')
brigade_count = cur.fetchone()[0]
print('brigade rows:', brigade_count)

# Проверяем, есть ли испытатели
cur.execute('SELECT COUNT(*) FROM tester')
tester_count = cur.fetchone()[0]
print('tester rows:', tester_count)

# Если нет сотрудников, добавляем всех
if emp_count == 0:
    print('=== Adding employees ===')
    # Рабочие
    cur.execute('''
    INSERT INTO employee (id_employee, last_name, first_name, middle_name, birth_date, education, hire_date, prior_exp, address, phone, salary) VALUES
    (101, 'Ivanov', 'Ivan', 'Ivanovich', '1985-03-15', 'Secondary Technical', '2010-06-01', 3, 'Moscow, Lenina 10-15', '+7-903-123-4567', 45000),
    (102, 'Petrov', 'Sergey', 'Petrovich', '1990-07-22', 'Secondary Technical', '2015-03-10', 2, 'Moscow, Gagarina 25-30', '+7-903-234-5678', 42000),
    (103, 'Sidorov', 'Aleksandr', 'Sergeevich', '1988-11-05', 'Secondary Technical', '2012-09-15', 4, 'Moscow, Pushkina 5-12', '+7-903-345-6789', 48000),
    (104, 'Smirnov', 'Dmitry', 'Vladimirovich', '1992-04-18', 'Secondary Technical', '2018-01-20', 1, 'Moscow, Kirova 15-8', '+7-903-456-7890', 40000),
    (105, 'Kozlov', 'Andrey', 'Mikhailovich', '1987-09-30', 'Secondary Technical', '2011-05-10', 5, 'Moscow, Sovetskaya 20-45', '+7-903-567-8901', 50000),
    (106, 'Morozov', 'Viktor', 'Petrovich', '1991-12-12', 'Secondary Technical', '2016-08-25', 2, 'Moscow, Oktyabrskaya 8-22', '+7-903-678-9012', 43000),
    (107, 'Novikov', 'Mikhail', 'Andreevich', '1989-06-08', 'Secondary Technical', '2014-02-14', 3, 'Moscow, Mira 12-18', '+7-903-789-0123', 46000),
    (201, 'Volkov', 'Alexey', 'Nikolaevich', '1980-02-20', 'Higher Technical', '2008-04-01', 8, 'Moscow, Tverskaya 5-10', '+7-905-111-2233', 75000),
    (202, 'Lebedev', 'Stanislav', 'Ivanovich', '1983-08-14', 'Higher Technical', '2010-07-15', 6, 'Moscow, Arbat 15-25', '+7-905-222-3344', 70000),
    (203, 'Orlov', 'Nikolay', 'Dmitrievich', '1978-05-25', 'Higher Technical', '2005-09-01', 10, 'Moscow, Petrovka 8-12', '+7-905-333-4455', 80000),
    (204, 'Fedorov', 'Pavel', 'Alexeevich', '1985-11-10', 'Higher Technical', '2012-03-20', 5, 'Moscow, Smolenskaya 22-30', '+7-905-444-5566', 68000),
    (205, 'Mikhailov', 'Roman', 'Sergeevich', '1982-03-28', 'Higher Technical', '2009-06-10', 7, 'Moscow, Kuibysheva 18-40', '+7-905-555-6677', 72000),
    (206, 'Vasiliev', 'Igor', 'Viktorovich', '1986-07-05', 'Higher Technical', '2011-11-05', 4, 'Moscow, Gorkovo 30-15', '+7-905-666-7788', 69000),
    (207, 'Zaitsev', 'Oleg', 'Pavlovich', '1984-01-15', 'Higher Technical', '2010-02-28', 6, 'Moscow, Bolshevskaya 10-8', '+7-905-777-8899', 71000),
    (301, 'Solovyov', 'Yuri', 'Andreevich', '1988-09-12', 'Higher Technical', '2013-05-15', 4, 'Moscow, Novy Arbat 5-20', '+7-906-111-2233', 55000),
    (302, 'Pavlov', 'Kirill', 'Mikhailovich', '1990-04-20', 'Higher Technical', '2015-08-10', 3, 'Moscow, Leninsky 45-60', '+7-906-222-3344', 52000),
    (303, 'Sokolov', 'Maxim', 'Dmitrievich', '1987-12-08', 'Higher Technical', '2012-02-20', 5, 'Moscow, Prospect Mira 30-25', '+7-906-333-4455', 58000),
    (304, 'Popov', 'Artur', 'Vladimirovich', '1992-06-15', 'Higher Technical', '2017-04-05', 2, 'Moscow, Kalinina 12-10', '+7-906-444-5566', 50000),
    (305, 'Kuznetsov', 'Denis', 'Aleksandrovich', '1989-08-22', 'Higher Technical', '2014-09-15', 4, 'Moscow, Chkalova 8-15', '+7-906-555-6677', 54000)
    ON CONFLICT (id_employee) DO NOTHING
    ''')
    conn.commit()
    print('OK: employees added')

# Если нет бригад, добавляем их (сначала без foreman из-за циклической зависимости)
if brigade_count == 0:
    print('=== Adding brigades (without foreman first) ===')
    cur.execute('''
    INSERT INTO brigade (id_brigade, name, id_section, id_foreman) VALUES
    (1, 'Brigade 1 - Assembly', 1, NULL),
    (2, 'Brigade 2 - Welding', 2, NULL),
    (3, 'Brigade 3 - Engine Test', 3, NULL),
    (4, 'Brigade 4 - Machining', 5, NULL),
    (5, 'Brigade 5 - Electronics', 6, NULL)
    ON CONFLICT DO NOTHING
    ''')
    conn.commit()
    print('OK: brigades added')

# Теперь обновляем бригады с foreman (после того как worker уже существует)
print('=== Updating brigades with foremen ===')
cur.execute('UPDATE brigade SET id_foreman = 102 WHERE id_brigade = 1')
cur.execute('UPDATE brigade SET id_foreman = 104 WHERE id_brigade = 2')
cur.execute('UPDATE brigade SET id_foreman = 107 WHERE id_brigade = 3')
cur.execute('UPDATE brigade SET id_foreman = 107 WHERE id_brigade = 4')
cur.execute('UPDATE brigade SET id_foreman = 107 WHERE id_brigade = 5')
conn.commit()
print('OK: brigades updated with foremen')

# Если нет worker, добавляем их (после бригад, чтобы FK работал)
if worker_count == 0:
    print('=== Adding workers ===')
    cur.execute('''
    INSERT INTO worker (id_employee, profession, rank, is_foreman, id_brigade) VALUES
    (101, 'Fitter', 4, false, 1),
    (102, 'Welder', 5, true, 1),
    (103, 'Fitter', 5, false, 2),
    (104, 'CNC Operator', 4, true, 2),
    (105, 'Electrician', 6, false, 3),
    (106, 'Welder', 4, false, 3),
    (107, 'Inspector', 5, true, 4)
    ON CONFLICT (id_employee) DO NOTHING
    ''')
    conn.commit()
    print('OK: workers added')

# Если нет испытателей, добавляем их
if tester_count == 0:
    print('=== Adding testers ===')
    cur.execute('''
    INSERT INTO tester (id_employee, specialization, id_lab) VALUES
    (301, 'Engine Testing', 2),
    (302, 'Vibration Testing', 4),
    (303, 'Quality Control', 1),
    (304, 'Environmental Testing', 5),
    (305, 'Materials Testing', 3)
    ON CONFLICT (id_employee) DO NOTHING
    ''')
    conn.commit()
    print('OK: testers added')

# Добавляем tester_equipment
cur.execute('SELECT COUNT(*) FROM tester_equipment')
te_count = cur.fetchone()[0]
print('tester_equipment rows:', te_count)

if te_count == 0:
    print('=== Adding tester_equipment ===')
    cur.execute('''
    INSERT INTO tester_equipment (id_tester, id_equipment, assignment_date) VALUES
    (301, 2, '2024-01-15'),
    (301, 7, '2024-01-15'),
    (302, 1, '2024-02-01'),
    (303, 5, '2024-01-10'),
    (303, 6, '2024-01-10'),
    (304, 4, '2024-03-01'),
    (305, 3, '2024-02-15')
    ON CONFLICT DO NOTHING
    ''')
    conn.commit()
    print('OK: tester_equipment added')

# Добавляем test_execution
cur.execute('SELECT COUNT(*) FROM test_execution')
test_exec_count = cur.fetchone()[0]
print('test_execution rows:', test_exec_count)

if test_exec_count == 0:
    print('=== Adding test_execution ===')
    cur.execute('''
    INSERT INTO test_execution (id_test_execution, serial_number, id_test_step, start_date, end_date, result) VALUES
    (1, 1006, 1, '2024-05-06', '2024-05-08', 'passed'),
    (2, 1006, 2, '2024-05-09', NULL, 'in_progress'),
    (3, 1007, 1, '2024-05-09', '2024-05-11', 'passed'),
    (4, 1007, 2, '2024-05-12', NULL, 'in_progress'),
    (5, 1001, 1, '2024-03-11', '2024-03-13', 'passed'),
    (6, 1001, 2, '2024-03-14', '2024-03-16', 'passed'),
    (7, 1001, 3, '2024-03-17', '2024-03-18', 'passed'),
    (8, 1002, 1, '2024-03-21', '2024-03-23', 'passed'),
    (9, 1002, 2, '2024-03-24', '2024-03-26', 'passed'),
    (10, 1002, 3, '2024-03-27', '2024-03-28', 'passed')
    ON CONFLICT DO NOTHING
    ''')
    conn.commit()
    print('OK: test_execution added')

# Проверяем view_testers
cur.execute('SELECT COUNT(*) FROM view_testers')
view_count = cur.fetchone()[0]
print('view_testers rows:', view_count)

print('=== OK: Готово ===')
cur.close()
conn.close()
