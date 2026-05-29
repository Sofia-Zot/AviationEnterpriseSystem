--цеха
INSERT INTO shop (id_shop, name) VALUES
(1, 'Shop 1 - Aircraft Assembly'),
(2, 'Shop 2 - Engine Manufacturing'),
(3, 'Shop 3 - Component Production'),
(4, 'Shop 4 - Final Assembly'),
(5, 'Shop 5 - Testing Center');

--лаборатории
INSERT INTO laboratory (id_lab, type, name) VALUES
(1, 'Quality Control', 'Lab 1 - Quality Control'),
(2, 'Engine Test', 'Lab 2 - Engine Test Stand'),
(3, 'Materials', 'Lab 3 - Materials Analysis'),
(4, 'Vibration', 'Lab 4 - Vibration Testing'),
(5, 'Environmental', 'Lab 5 - Environmental Test');

--категории изделий
INSERT INTO product_category (id_category, name) VALUES
(1, 'Aircraft'),
(2, 'Engine'),
(3, 'Avionics'),
(4, 'Landing Gear'),
(5, 'Components');

--сотрудники
INSERT INTO employee (id_employee, last_name, first_name, middle_name, birth_date, education, hire_date, prior_exp, address, phone, salary) VALUES
-- рабочие
(101, 'Ivanov', 'Ivan', 'Ivanovich', '1985-03-15', 'Secondary Technical', '2010-06-01', 3, 'Moscow, Lenina 10-15', '+7-903-123-4567', 45000),
(102, 'Petrov', 'Sergey', 'Petrovich', '1990-07-22', 'Secondary Technical', '2015-03-10', 2, 'Moscow, Gagarina 25-30', '+7-903-234-5678', 42000),
(103, 'Sidorov', 'Aleksandr', 'Sergeevich', '1988-11-05', 'Secondary Technical', '2012-09-15', 4, 'Moscow, Pushkina 5-12', '+7-903-345-6789', 48000),
(104, 'Smirnov', 'Dmitry', 'Vladimirovich', '1992-04-18', 'Secondary Technical', '2018-01-20', 1, 'Moscow, Kirova 15-8', '+7-903-456-7890', 40000),
(105, 'Kozlov', 'Andrey', 'Mikhailovich', '1987-09-30', 'Secondary Technical', '2011-05-10', 5, 'Moscow, Sovetskaya 20-45', '+7-903-567-8901', 50000),
(106, 'Morozov', 'Viktor', 'Petrovich', '1991-12-12', 'Secondary Technical', '2016-08-25', 2, 'Moscow, Oktyabrskaya 8-22', '+7-903-678-9012', 43000),
(107, 'Novikov', 'Mikhail', 'Andreevich', '1989-06-08', 'Secondary Technical', '2014-02-14', 3, 'Moscow, Mira 12-18', '+7-903-789-0123', 46000),

-- итр
(201, 'Volkov', 'Alexey', 'Nikolaevich', '1980-02-20', 'Higher Technical', '2008-04-01', 8, 'Moscow, Tverskaya 5-10', '+7-905-111-2233', 75000),
(202, 'Lebedev', 'Stanislav', 'Ivanovich', '1983-08-14', 'Higher Technical', '2010-07-15', 6, 'Moscow, Arbat 15-25', '+7-905-222-3344', 70000),
(203, 'Orlov', 'Nikolay', 'Dmitrievich', '1978-05-25', 'Higher Technical', '2005-09-01', 10, 'Moscow, Petrovka 8-12', '+7-905-333-4455', 80000),
(204, 'Fedorov', 'Pavel', 'Alexeevich', '1985-11-10', 'Higher Technical', '2012-03-20', 5, 'Moscow, Smolenskaya 22-30', '+7-905-444-5566', 68000),
(205, 'Mikhailov', 'Roman', ' Sergeevich', '1982-03-28', 'Higher Technical', '2009-06-10', 7, 'Moscow, Kuibysheva 18-40', '+7-905-555-6677', 72000),
(206, 'Vasiliev', 'Igor', 'Viktorovich', '1986-07-05', 'Higher Technical', '2011-11-05', 4, 'Moscow, Gorkovo 30-15', '+7-905-666-7788', 69000),
(207, 'Zaitsev', 'Oleg', 'Pavlovich', '1984-01-15', 'Higher Technical', '2010-02-28', 6, 'Moscow, Bolshevskaya 10-8', '+7-905-777-8899', 71000),

--испытатели
(301, 'Solovyov', 'Yuri', 'Andreevich', '1988-09-12', 'Higher Technical', '2013-05-15', 4, 'Moscow, Novy Arbat 5-20', '+7-906-111-2233', 55000),
(302, 'Pavlov', 'Kirill', 'Mikhailovich', '1990-04-20', 'Higher Technical', '2015-08-10', 3, 'Moscow, Leninsky 45-60', '+7-906-222-3344', 52000),
(303, 'Sokolov', 'Maxim', 'Dmitrievich', '1987-12-08', 'Higher Technical', '2012-02-20', 5, 'Moscow, Prospect Mira 30-25', '+7-906-333-4455', 58000),
(304, 'Popov', 'Artur', 'Vladimirovich', '1992-06-15', 'Higher Technical', '2017-04-05', 2, 'Moscow, Kalinina 12-10', '+7-906-444-5566', 50000),
(305, 'Kuznetsov', 'Denis', 'Aleksandrovich', '1989-08-22', 'Higher Technical', '2014-09-15', 4, 'Moscow, Chkalova 8-15', '+7-906-555-6677', 54000);

--участки
INSERT INTO section (id_section, name, id_shop) VALUES
(1, 'Assembly Line 1', 1),
(2, 'Welding Shop', 1),
(3, 'Engine Test Stand', 2),
(4, 'Engine Assembly', 2),
(5, 'Component Machining', 3),
(6, 'Electronics Assembly', 3),
(7, 'Final Inspection', 4),
(8, 'Quality Control', 5);

--итр
INSERT INTO engineer (id_employee, category, position) VALUES
(201, 'Engineer', 'Chief Engineer'),
(202, 'Engineer', 'Senior Engineer'),
(203, 'Technologist', 'Chief Technologist'),
(204, 'Technologist', 'Technologist'),
(205, 'Engineer', 'Design Engineer'),
(206, 'Technician', 'Senior Technician'),
(207, 'Master', 'Master');

--рабочие
INSERT INTO worker (id_employee, profession, rank, is_foreman, id_brigade) VALUES
(101, 'Fitter', 4, FALSE, 1),
(102, 'Welder', 5, TRUE, 1),
(103, 'Fitter', 5, FALSE, 2),
(104, 'CNC Operator', 4, TRUE, 2),
(105, 'Electrician', 6, FALSE, 3),
(106, 'Welder', 4, FALSE, 3),
(107, 'Inspector', 5, TRUE, 4);

--бригады
INSERT INTO brigade (id_brigade, name, id_section, id_foreman) VALUES
(1, 'Brigade 1 - Assembly', 1, 102),
(2, 'Brigade 2 - Welding', 2, 104),
(3, 'Brigade 3 - Engine Test', 3, 107),
(4, 'Brigade 4 - Machining', 5, 107),
(5, 'Brigade 5 - Electronics', 6, 107);

--испытатели
INSERT INTO tester (id_employee, specialization, id_lab) VALUES
(301, 'Engine Testing', 2),
(302, 'Vibration Testing', 4),
(303, 'Quality Control', 1),
(304, 'Environmental Testing', 5),
(305, 'Materials Testing', 3);

--виды изделий
INSERT INTO product_type (id_type, name, id_category) VALUES
(1, 'Boeing 737-800', 1),
(2, 'Airbus A320neo', 1),
(3, 'CFM56-7B Engine', 2),
(4, 'LEAP-1A Engine', 2),
(5, 'Flight Control System', 3),
(6, 'Main Landing Gear', 4),
(7, 'Hydraulic Pump', 5),
(8, 'Fuel Control Unit', 5);

--иделия экземпляры
INSERT INTO product_instance (serial_number, status, id_shop, id_type, weight, material, batch) VALUES
(1001, 'ready', 1, 1, 45000.00, 'Aluminum Alloy', 'BATCH-2024-001'),
(1002, 'ready', 1, 1, 46500.00, 'Aluminum Alloy', 'BATCH-2024-001'),
(1003, 'ready', 1, 1, 44000.00, 'Aluminum Alloy', 'BATCH-2024-001'),
(1004, 'in_assembly', 1, 2, 42000.00, 'Aluminum Alloy', 'BATCH-2024-002'),
(1005, 'in_assembly', 1, 2, 43500.00, 'Aluminum Alloy', 'BATCH-2024-002'),
(1006, 'under_test', 2, 3, 2500.00, 'Steel/Titanium', 'BATCH-2024-003'),
(1007, 'under_test', 2, 3, 2600.00, 'Steel/Titanium', 'BATCH-2024-003'),
(1008, 'in_assembly', 2, 4, 2800.00, 'Steel/Titanium', 'BATCH-2024-003'),
(1009, 'in_assembly', 3, 5, 150.00, 'Composite/Electronics', 'BATCH-2024-004'),
(1010, 'in_assembly', 3, 5, 160.00, 'Composite/Electronics', 'BATCH-2024-004'),
(1011, 'ready', 4, 6, 800.00, 'Steel/Aluminum', 'BATCH-2024-002'),
(1012, 'ready', 4, 6, 820.00, 'Steel/Aluminum', 'BATCH-2024-002'),
(1013, 'in_assembly', 5, 7, 95.00, 'Steel', 'BATCH-2024-005'),
(1014, 'in_assembly', 5, 8, 45.00, 'Steel/Aluminum', 'BATCH-2024-005'),
(1015, 'under_test', 5, 7, 98.00, 'Steel', 'BATCH-2024-005');

--особые типы
INSERT INTO aircraft_type (id_type, purpose, parameters) VALUES
(1, 'Commercial passenger aircraft', 'Range: 5765 km, Capacity: 162-189 passengers'),
(2, 'Commercial passenger aircraft', 'Range: 6500 km, Capacity: 167-194 passengers');

INSERT INTO helicopter_type (id_type, purpose, parameters) VALUES
-- (если нужны вертолёты)
;

INSERT INTO rocket_type (id_type, purpose, parameters) VALUES
-- (если нужны ракеты)
;

--лаборатории обслуживают цеха
INSERT INTO shop_lab (id_shop, id_lab) VALUES
(1, 1),
(1, 3),
(2, 2),
(2, 4),
(3, 1),
(4, 5),
(5, 1),
(5, 2);

--оборудование лабораторий
INSERT INTO equipment (id_equipment, name, model, id_lab) VALUES
(1, 'Vibration Tester', 'VT-2000', 4),
(2, 'Pressure Test Stand', 'PTS-500', 2),
(3, 'Spectral Analyzer', 'SA-1000', 3),
(4, 'Climate Chamber', 'CC-300', 5),
(5, 'CMM Machine', 'CMM-Hexagon', 1),
(6, 'Ultrasonic Tester', 'UT-500', 1),
(7, 'Torque Tester', 'TT-200', 2);

--оборудование испытателей
INSERT INTO tester_equipment (id_tester, id_equipment, assignment_date) VALUES
(301, 2, '2024-01-15'),
(301, 7, '2024-01-15'),
(302, 1, '2024-02-01'),
(303, 5, '2024-01-10'),
(303, 6, '2024-01-10'),
(304, 4, '2024-03-01'),
(305, 3, '2024-02-15');

--тк
INSERT INTO tech_card (id_card, id_type) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 5),
(6, 6),
(7, 7),
(8, 8);

--перечень работ учатсков
INSERT INTO section_work_list (id_work, id_section, work_name, description) VALUES
(1, 1, 'Fuselage Assembly', 'Assembly of main fuselage sections'),
(2, 1, 'Wing Installation', 'Installation and alignment of wings'),
(3, 2, 'Welding Structures', 'Welding of structural components'),
(4, 3, 'Engine Test Run', 'Full engine test run under load'),
(5, 4, 'Engine Assembly', 'Assembly of engine components'),
(6, 5, 'Part Machining', 'CNC machining of parts'),
(7, 6, 'Electronics Installation', 'Installation of electronic systems'),
(8, 7, 'Final Inspection', 'Final quality inspection');

--этапы работ в тк
INSERT INTO work_step (id_step, id_card, id_work, step_number) VALUES
(1, 1, 1, 1),
(2, 1, 2, 2),
(3, 2, 1, 1),
(4, 2, 2, 2),
(5, 3, 4, 1),
(6, 3, 5, 2),
(7, 4, 4, 1),
(8, 4, 5, 2),
(9, 5, 6, 1),
(10, 5, 7, 2),
(11, 6, 6, 1),
(12, 6, 8, 2);

--выполнение работ
INSERT INTO work_execution (id_execution, serial_number, id_step, start_date, end_date, status) VALUES
-- Продукт 1001 (готовый)
(1, 1001, 1, '2024-01-10', '2024-02-15', 'completed'),
(2, 1001, 2, '2024-02-16', '2024-03-10', 'completed'),
-- Продукт 1002 (готовый)
(3, 1002, 1, '2024-02-01', '2024-03-01', 'completed'),
(4, 1002, 2, '2024-03-02', '2024-03-20', 'completed'),
-- Продукт 1003 (готовый)
(5, 1003, 1, '2024-02-15', '2024-03-15', 'completed'),
(6, 1003, 2, '2024-03-16', '2024-03-25', 'completed'),
-- Продукт 1004 (в сборке)
(7, 1004, 3, '2024-03-15', '2024-04-10', 'completed'),
(8, 1004, 4, '2024-04-11', NULL, 'in_progress'),
-- Продукт 1005 (в сборке)
(9, 1005, 3, '2024-03-20', '2024-04-15', 'completed'),
(10, 1005, 4, '2024-04-16', NULL, 'in_progress'),
-- Продукт 1006 (на испытаниях)
(11, 1006, 5, '2024-04-01', '2024-04-20', 'completed'),
(12, 1006, 6, '2024-04-21', '2024-05-05', 'completed'),
-- Продукт 1007 (на испытаниях)
(13, 1007, 5, '2024-04-05', '2024-04-25', 'completed'),
(14, 1007, 6, '2024-04-26', '2024-05-08', 'completed'),
-- Продукт 1008 (в сборке)
(15, 1008, 7, '2024-04-10', NULL, 'in_progress'),
-- Продукт 1009 (в сборке)
(16, 1009, 9, '2024-04-15', NULL, 'in_progress'),
-- Продукт 1010 (в сборке)
(17, 1010, 9, '2024-04-18', NULL, 'in_progress'),
-- Продукт 1011 (готовый)
(18, 1011, 11, '2024-02-10', '2024-03-05', 'completed'),
(19, 1011, 12, '2024-03-06', '2024-03-20', 'completed'),
-- Продукт 1012 (готовый)
(20, 1012, 11, '2024-02-15', '2024-03-10', 'completed'),
(21, 1012, 12, '2024-03-11', '2024-03-25', 'completed'),
-- Продукт 1013 (в сборке)
(22, 1013, 1, '2024-04-20', NULL, 'in_progress'),
-- Продукт 1014 (в сборке)
(23, 1014, 3, '2024-04-22', NULL, 'in_progress'),
-- Продукт 1015 (на испытаниях)
(24, 1015, 5, '2024-04-25', '2024-05-10', 'completed'),
(25, 1015, 6, '2024-05-11', NULL, 'in_progress');

--испытательная карта
INSERT INTO test_card (id_test_card, id_type) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4);

--перечень испытаний
INSERT INTO test_work_list (id_test_work, id_equipment, test_name) VALUES
(1, 1, 'Vibration Test'),
(2, 2, 'Pressure Test'),
(3, 3, 'Material Analysis'),
(4, 4, 'Environmental Test'),
(5, 5, 'Dimensional Check'),
(6, 6, 'Ultrasonic Test'),
(7, 7, 'Torque Test');

--этапы испытаний
INSERT INTO test_step (id_step, id_test_card, id_test_work, step_number) VALUES
(1, 1, 1, 1),
(2, 1, 2, 2),
(3, 1, 5, 3),
(4, 2, 1, 1),
(5, 2, 2, 2),
(6, 3, 2, 1),
(7, 3, 3, 2),
(8, 4, 2, 1),
(9, 4, 7, 2);

--выполнение испытаний
INSERT INTO test_execution (id_test_execution, serial_number, id_test_step, start_date, end_date, result) VALUES
-- Продукт 1006 (на испытаниях - passed)
(1, 1006, 1, '2024-05-06', '2024-05-08', 'passed'),
(2, 1006, 2, '2024-05-09', NULL, 'in_progress'),
-- Продукт 1007 (на испытаниях - passed)
(3, 1007, 1, '2024-05-09', '2024-05-11', 'passed'),
(4, 1007, 2, '2024-05-12', NULL, 'in_progress'),
-- Продукт 1001 (прошёл все испытания)
(5, 1001, 1, '2024-03-11', '2024-03-13', 'passed'),
(6, 1001, 2, '2024-03-14', '2024-03-16', 'passed'),
(7, 1001, 3, '2024-03-17', '2024-03-18', 'passed'),
-- Продукт 1002 (прошёл все испытания)
(8, 1002, 1, '2024-03-21', '2024-03-23', 'passed'),
(9, 1002, 2, '2024-03-24', '2024-03-26', 'passed'),
(10, 1002, 3, '2024-03-27', '2024-03-28', 'passed'),
-- Продукт 1003 (прошёл все испытания)
(11, 1003, 1, '2024-03-26', '2024-03-28', 'passed'),
(12, 1003, 2, '2024-03-29', '2024-03-31', 'passed'),
(13, 1003, 3, '2024-04-01', '2024-04-02', 'passed'),
-- Продукт 1011 (прошёл все испытания)
(14, 1011, 4, '2024-03-21', '2024-03-23', 'passed'),
(15, 1011, 5, '2024-03-24', '2024-03-25', 'passed'),
-- Продукт 1012 (прошёл все испытания)
(16, 1012, 4, '2024-03-26', '2024-03-28', 'passed'),
(17, 1012, 5, '2024-03-29', '2024-03-30', 'passed'),
-- Продукт 1015 (на испытаниях)
(18, 1015, 6, '2024-05-12', '2024-05-14', 'passed'),
(19, 1015, 7, '2024-05-15', NULL, 'in_progress');


