--добавить начальника на участок
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'section'
          AND column_name = 'id_manager'
    ) THEN
        ALTER TABLE section ADD COLUMN id_manager INT;
        ALTER TABLE section ADD CONSTRAINT fk_section_manager
            FOREIGN KEY (id_manager) REFERENCES engineer(id_employee)
            ON DELETE SET NULL ON UPDATE CASCADE;
        -- Optional: unique constraint so one engineer manages max one section
        ALTER TABLE section ADD CONSTRAINT uq_section_manager UNIQUE (id_manager);
    END IF;
END $$;

--назначить инженера на участок
UPDATE section SET id_manager = 201 WHERE id_section = 1 AND id_manager IS NULL;
UPDATE section SET id_manager = 202 WHERE id_section = 2 AND id_manager IS NULL;
UPDATE section SET id_manager = 203 WHERE id_section = 3 AND id_manager IS NULL;
UPDATE section SET id_manager = 204 WHERE id_section = 4 AND id_manager IS NULL;
UPDATE section SET id_manager = 205 WHERE id_section = 5 AND id_manager IS NULL;
UPDATE section SET id_manager = 206 WHERE id_section = 6 AND id_manager IS NULL;
UPDATE section SET id_manager = 207 WHERE id_section = 7 AND id_manager IS NULL;
UPDATE section SET id_manager = 201 WHERE id_section = 8 AND id_manager IS NULL;


-- view_sections_with_managers
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

-- view_completed_products
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
GROUP BY pi.serial_number, pt.name, pi.id_shop, sh.name, pt.id_category, pc.name;

-- view_workers
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

-- view_engineers
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

-- view_product_types_by_shop
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

-- view_product_work_steps
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

-- view_brigade_members
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

-- view_masters
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

-- view_products_in_assembly
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

-- view_brigades_for_product
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

-- view_labs_for_product
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

-- view_tested_products
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

-- view_testers
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

-- view_equipment_for_tests
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

-- view_products_in_assembly_summary
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
GROUP BY pi.id_shop, sh.name, sec.id_section, sec.name, pt.id_category, pc.name;

