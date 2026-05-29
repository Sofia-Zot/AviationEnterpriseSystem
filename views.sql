DROP VIEW IF EXISTS view_product_types_by_shop CASCADE;

CREATE VIEW view_product_types_by_shop AS
SELECT DISTINCT
    s.id_shop,
    s.name AS shop_name,
    pc.id_category,
    pc.name AS category_name,
    pt.id_type,
    pt.name AS product_type_name
FROM product_type pt
JOIN product_category pc ON pt.id_category = pc.id_category
JOIN product_instance pi ON pi.id_type = pt.id_type
JOIN shop s ON pi.id_shop = s.id_shop;

COMMENT ON VIEW view_product_types_by_shop IS
'Виды изделий по цехам и категориям. Фильтрация в клиенте: WHERE id_shop = N [AND id_category = M].';


-- Для каждого готового изделия ровно одна строка.
-- completion_date = максимальная дата из всех этапов work_execution.
DROP VIEW IF EXISTS view_completed_products CASCADE;

CREATE VIEW view_completed_products AS
SELECT
    pi.serial_number,
    pt.name AS product_type_name,
    pi.id_shop,
    sh.name AS shop_name,
    pt.id_category,
    pc.name AS category_name,
    MAX(we.end_date) AS completion_date
FROM product_instance pi
JOIN product_type pt ON pi.id_type = pt.id_type
JOIN product_category pc ON pt.id_category = pc.id_category
JOIN shop sh ON pi.id_shop = sh.id_shop
LEFT JOIN work_execution we ON we.serial_number = pi.serial_number
WHERE pi.status = 'ready'
GROUP BY
    pi.serial_number,
    pt.name,
    pi.id_shop,
    sh.name,
    pt.id_category,
    pc.name;

COMMENT ON VIEW view_completed_products IS
'Изделия со статусом ready (одна строка на изделие, completion_date = MAX(end_date)). Фильтрация в клиенте: WHERE id_shop = N AND completion_date BETWEEN ... AND ... [AND id_category = M].';



DROP VIEW IF EXISTS view_workers CASCADE;

CREATE VIEW view_workers AS
SELECT
    e.id_employee,
    e.last_name,
    e.first_name,
    e.middle_name,
    w.profession,
    w.rank,
    w.is_foreman,
    w.id_brigade,
    b.name AS brigade_name,
    b.id_section,
    sec.name AS section_name,
    sec.id_shop,
    sh.name AS shop_name
FROM employee e
JOIN worker w ON e.id_employee = w.id_employee
LEFT JOIN brigade b ON w.id_brigade = b.id_brigade
LEFT JOIN section sec ON b.id_section = sec.id_section
LEFT JOIN shop sh ON sec.id_shop = sh.id_shop;

COMMENT ON VIEW view_workers IS
'Кадровый состав рабочих. Фильтрация в клиенте: WHERE id_shop = N [AND id_section = M].';



DROP VIEW IF EXISTS view_engineers CASCADE;

CREATE VIEW view_engineers AS
SELECT
    e.id_employee,
    e.last_name,
    e.first_name,
    e.middle_name,
    eng.category,
    eng.position
FROM employee e
JOIN engineer eng ON e.id_employee = eng.id_employee;

COMMENT ON VIEW view_engineers IS
'Кадровый состав ИТР. Фильтрация в клиенте: WHERE position LIKE ...';



-- Требуется поле section.id_manager (INT, FK → engineer(id_employee), UNIQUE).
-- См. скрипт fix_section_and_views.sql для ALTER TABLE.
DROP VIEW IF EXISTS view_sections_with_managers CASCADE;

CREATE VIEW view_sections_with_managers AS
SELECT
    sec.id_section,
    sec.name AS section_name,
    sec.id_shop,
    sh.name AS shop_name,
    e.id_employee AS manager_id,
    e.last_name AS manager_last_name,
    e.first_name AS manager_first_name,
    e.middle_name AS manager_middle_name,
    eng.position AS manager_position
FROM section sec
JOIN shop sh ON sec.id_shop = sh.id_shop
LEFT JOIN engineer eng ON sec.id_manager = eng.id_employee
LEFT JOIN employee e ON eng.id_employee = e.id_employee;

COMMENT ON VIEW view_sections_with_managers IS
'Участки цехов и их начальники (через section.id_manager → engineer). Фильтрация в клиенте: WHERE id_shop = N.';


DROP VIEW IF EXISTS view_product_work_steps CASCADE;

CREATE VIEW view_product_work_steps AS
SELECT
    pi.serial_number,
    swl.work_name,
    swl.description,
    ws.step_number,
    we.status AS execution_status,
    we.start_date,
    we.end_date,
    swl.id_section,
    sec.name AS section_name
FROM product_instance pi
JOIN work_execution we ON we.serial_number = pi.serial_number
JOIN work_step ws ON we.id_step = ws.id_step
JOIN section_work_list swl ON ws.id_work = swl.id_work
LEFT JOIN section sec ON swl.id_section = sec.id_section;

COMMENT ON VIEW view_product_work_steps IS
'Перечень работ (этапов сборки) для каждого изделия. Фильтрация в клиенте: WHERE serial_number = N ORDER BY step_number.';

DROP VIEW IF EXISTS view_brigade_members CASCADE;

CREATE VIEW view_brigade_members AS
SELECT
    b.id_brigade,
    b.name AS brigade_name,
    b.id_section,
    sec.name AS section_name,
    sec.id_shop,
    sh.name AS shop_name,
    e.id_employee,
    e.last_name,
    e.first_name,
    e.middle_name,
    w.profession,
    w.rank,
    w.is_foreman
FROM brigade b
JOIN section sec ON b.id_section = sec.id_section
JOIN shop sh ON sec.id_shop = sh.id_shop
JOIN worker w ON w.id_brigade = b.id_brigade
JOIN employee e ON w.id_employee = e.id_employee;

COMMENT ON VIEW view_brigade_members IS
'Состав бригад (рабочие). Фильтрация в клиенте: WHERE id_shop = N [AND id_section = M].';


DROP VIEW IF EXISTS view_masters CASCADE;

CREATE VIEW view_masters AS
SELECT
    e.id_employee,
    e.last_name,
    e.first_name,
    e.middle_name,
    eng.category,
    eng.position
FROM employee e
JOIN engineer eng ON e.id_employee = eng.id_employee
WHERE eng.position = 'Master';

COMMENT ON VIEW view_masters IS
'Список мастеров (engineer с position = Master). Фильтрация в клиенте: по цеху/участку через дополнительные JOIN в запросе.';


DROP VIEW IF EXISTS view_products_in_assembly CASCADE;

CREATE VIEW view_products_in_assembly AS
SELECT
    pi.serial_number,
    pt.name AS product_type_name,
    pt.id_category,
    pc.name AS category_name,
    pi.id_shop,
    sh.name AS shop_name,
    pi.status
FROM product_instance pi
JOIN product_type pt ON pi.id_type = pt.id_type
JOIN product_category pc ON pt.id_category = pc.id_category
JOIN shop sh ON pi.id_shop = sh.id_shop
WHERE pi.status = 'in_assembly';

COMMENT ON VIEW view_products_in_assembly IS
'Изделия, находящиеся в сборке (status = in_assembly). Фильтрация в клиенте: WHERE id_shop = N [AND id_category = M].';


-- Связь: work_execution → work_step → section_work_list → section → brigade
DROP VIEW IF EXISTS view_brigades_for_product CASCADE;

CREATE VIEW view_brigades_for_product AS
SELECT DISTINCT
    pi.serial_number,
    b.id_brigade,
    b.name AS brigade_name,
    sec.id_section,
    sec.name AS section_name,
    e.id_employee,
    e.last_name,
    e.first_name,
    e.middle_name,
    w.profession,
    w.rank
FROM product_instance pi
JOIN work_execution we ON we.serial_number = pi.serial_number
JOIN work_step ws ON we.id_step = ws.id_step
JOIN section_work_list swl ON ws.id_work = swl.id_work
JOIN section sec ON swl.id_section = sec.id_section
JOIN brigade b ON b.id_section = sec.id_section
JOIN worker w ON w.id_brigade = b.id_brigade
JOIN employee e ON w.id_employee = e.id_employee;

COMMENT ON VIEW view_brigades_for_product IS
'Бригады и их состав, участвующие в сборке изделия (через участок работ). Фильтрация в клиенте: WHERE serial_number = N.';


-- Связь: test_execution → test_step → test_work_list → equipment → laboratory
DROP VIEW IF EXISTS view_labs_for_product CASCADE;

CREATE VIEW view_labs_for_product AS
SELECT DISTINCT
    pi.serial_number,
    l.id_lab,
    l.name AS lab_name,
    l.type AS lab_type
FROM product_instance pi
JOIN test_execution te ON te.serial_number = pi.serial_number
JOIN test_step ts ON te.id_test_step = ts.id_step
JOIN test_work_list twl ON ts.id_test_work = twl.id_test_work
JOIN equipment eq ON twl.id_equipment = eq.id_equipment
JOIN laboratory l ON eq.id_lab = l.id_lab;

COMMENT ON VIEW view_labs_for_product IS
'Лаборатории, участвующие в испытаниях изделия. Фильтрация в клиенте: WHERE serial_number = N.';


DROP VIEW IF EXISTS view_tested_products CASCADE;

CREATE VIEW view_tested_products AS
SELECT DISTINCT
    pi.serial_number,
    pt.name AS product_type_name,
    pt.id_category,
    pc.name AS category_name,
    l.id_lab,
    l.name AS lab_name,
    te.end_date AS test_date,
    te.result AS test_result
FROM product_instance pi
JOIN product_type pt ON pi.id_type = pt.id_type
JOIN product_category pc ON pt.id_category = pc.id_category
JOIN test_execution te ON te.serial_number = pi.serial_number
JOIN test_step ts ON te.id_test_step = ts.id_step
JOIN test_work_list twl ON ts.id_test_work = twl.id_test_work
JOIN equipment eq ON twl.id_equipment = eq.id_equipment
JOIN laboratory l ON eq.id_lab = l.id_lab
WHERE te.result = 'passed';

COMMENT ON VIEW view_tested_products IS
'Изделия, прошедшие испытания (result = passed). Фильтрация в клиенте: WHERE id_lab = N AND test_date BETWEEN ... AND ... [AND id_category = M].';


-- Связь: tester → tester_equipment → equipment → test_work_list → test_step → test_execution
DROP VIEW IF EXISTS view_testers CASCADE;

CREATE VIEW view_testers AS
SELECT DISTINCT
    e.id_employee AS id_tester,
    e.last_name,
    e.first_name,
    e.middle_name,
    t.specialization,
    eq.id_lab,
    l.name AS lab_name,
    pi.serial_number,
    pt.id_category,
    pc.name AS category_name,
    te.end_date AS test_date
FROM employee e
JOIN tester t ON e.id_employee = t.id_employee
JOIN tester_equipment teq ON t.id_employee = teq.id_tester
JOIN equipment eq ON teq.id_equipment = eq.id_equipment
JOIN test_work_list twl ON eq.id_equipment = twl.id_equipment
JOIN test_step ts ON twl.id_test_work = ts.id_test_work
JOIN test_execution te ON ts.id_step = te.id_test_step
JOIN product_instance pi ON te.serial_number = pi.serial_number
JOIN product_type pt ON pi.id_type = pt.id_type
JOIN product_category pc ON pt.id_category = pc.id_category;

COMMENT ON VIEW view_testers IS
'Испытатели и их участие в испытаниях. Фильтрация в клиенте: WHERE serial_number = N OR id_category = M OR id_lab = K.';


DROP VIEW IF EXISTS view_equipment_for_tests CASCADE;

CREATE VIEW view_equipment_for_tests AS
SELECT DISTINCT
    pi.serial_number,
    eq.id_equipment,
    eq.name AS equipment_name,
    eq.model AS equipment_model,
    l.id_lab,
    l.name AS lab_name
FROM product_instance pi
JOIN test_execution te ON te.serial_number = pi.serial_number
JOIN test_step ts ON te.id_test_step = ts.id_step
JOIN test_work_list twl ON ts.id_test_work = twl.id_test_work
JOIN equipment eq ON twl.id_equipment = eq.id_equipment
JOIN laboratory l ON eq.id_lab = l.id_lab;

COMMENT ON VIEW view_equipment_for_tests IS
'Оборудование, использованное при испытаниях изделий. Фильтрация в клиенте: WHERE serial_number = N [AND id_lab = M].';


DROP VIEW IF EXISTS view_products_in_assembly_summary CASCADE;

CREATE VIEW view_products_in_assembly_summary AS
SELECT
    pi.id_shop,
    sh.name AS shop_name,
    sec.id_section,
    sec.name AS section_name,
    pt.id_category,
    pc.name AS category_name,
    COUNT(*) AS product_count
FROM product_instance pi
JOIN product_type pt ON pi.id_type = pt.id_type
JOIN product_category pc ON pt.id_category = pc.id_category
JOIN shop sh ON pi.id_shop = sh.id_shop
LEFT JOIN work_execution we ON we.serial_number = pi.serial_number
LEFT JOIN work_step ws ON we.id_step = ws.id_step
LEFT JOIN section_work_list swl ON ws.id_work = swl.id_work
LEFT JOIN section sec ON swl.id_section = sec.id_section
WHERE pi.status = 'in_assembly'
GROUP BY
    pi.id_shop, sh.name,
    sec.id_section, sec.name,
    pt.id_category, pc.name;

COMMENT ON VIEW view_products_in_assembly_summary IS
'Сводка: количество изделий в сборке по цехам, участкам и категориям. Фильтрация в клиенте: WHERE id_shop = N [AND id_section = M].';
