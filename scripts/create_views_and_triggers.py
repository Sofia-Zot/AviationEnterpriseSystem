"""
Create all views and triggers via Python (avoids WIN1252 encoding issues).
Run: python scripts/create_views_and_triggers.py
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

# ============================================================
# 1. Views
# ============================================================

views = [
    ("view_product_types_by_shop", """
        SELECT DISTINCT s.id_shop, s.name AS shop_name, pc.id_category, pc.name AS category_name,
            pt.id_type, pt.name AS product_type_name
        FROM product_type pt
        JOIN product_category pc ON pt.id_category = pc.id_category
        JOIN product_instance pi ON pi.id_type = pt.id_type
        JOIN shop s ON pi.id_shop = s.id_shop
    """),
    ("view_completed_products", """
        SELECT pi.serial_number, pt.name AS product_type_name, pi.id_shop, sh.name AS shop_name,
            pt.id_category, pc.name AS category_name, MAX(we.end_date) AS completion_date
        FROM product_instance pi
        JOIN product_type pt ON pi.id_type = pt.id_type
        JOIN product_category pc ON pt.id_category = pc.id_category
        JOIN shop sh ON pi.id_shop = sh.id_shop
        LEFT JOIN work_execution we ON we.serial_number = pi.serial_number
        WHERE pi.status = 'ready'
        GROUP BY pi.serial_number, pt.name, pi.id_shop, sh.name, pt.id_category, pc.name
    """),
    ("view_workers", """
        SELECT e.id_employee, e.last_name, e.first_name, e.middle_name,
            w.profession, w.rank, w.is_foreman, w.id_brigade,
            b.name AS brigade_name, b.id_section, sec.name AS section_name, sec.id_shop, sh.name AS shop_name
        FROM employee e
        JOIN worker w ON e.id_employee = w.id_employee
        LEFT JOIN brigade b ON w.id_brigade = b.id_brigade
        LEFT JOIN section sec ON b.id_section = sec.id_section
        LEFT JOIN shop sh ON sec.id_shop = sh.id_shop
    """),
    ("view_engineers", """
        SELECT e.id_employee, e.last_name, e.first_name, e.middle_name,
            eng.category, eng.position
        FROM employee e
        JOIN engineer eng ON e.id_employee = eng.id_employee
    """),
    ("view_sections_with_managers", """
        SELECT sec.id_section, sec.name AS section_name, sec.id_shop, sh.name AS shop_name,
            e.id_employee AS manager_id, e.last_name AS manager_last_name,
            e.first_name AS manager_first_name, e.middle_name AS manager_middle_name,
            eng.position AS manager_position
        FROM section sec
        JOIN shop sh ON sec.id_shop = sh.id_shop
        LEFT JOIN engineer eng ON sec.id_manager = eng.id_employee
        LEFT JOIN employee e ON eng.id_employee = e.id_employee
    """),
    ("view_product_work_steps", """
        SELECT pi.serial_number, swl.work_name, swl.description, ws.step_number,
            we.status AS execution_status, we.start_date, we.end_date,
            swl.id_section, sec.name AS section_name
        FROM product_instance pi
        JOIN work_execution we ON we.serial_number = pi.serial_number
        JOIN work_step ws ON we.id_step = ws.id_step
        JOIN section_work_list swl ON ws.id_work = swl.id_work
        LEFT JOIN section sec ON swl.id_section = sec.id_section
    """),
    ("view_brigade_members", """
        SELECT b.id_brigade, b.name AS brigade_name, b.id_section, sec.name AS section_name,
            sec.id_shop, sh.name AS shop_name, e.id_employee, e.last_name, e.first_name,
            e.middle_name, w.profession, w.rank, w.is_foreman
        FROM brigade b
        JOIN section sec ON b.id_section = sec.id_section
        JOIN shop sh ON sec.id_shop = sh.id_shop
        JOIN worker w ON w.id_brigade = b.id_brigade
        JOIN employee e ON w.id_employee = e.id_employee
    """),
    ("view_masters", """
        SELECT e.id_employee, e.last_name, e.first_name, e.middle_name,
            eng.category, eng.position
        FROM employee e
        JOIN engineer eng ON e.id_employee = eng.id_employee
        WHERE eng.position = 'Master'
    """),
    ("view_products_in_assembly", """
        SELECT pi.serial_number, pt.name AS product_type_name, pt.id_category, pc.name AS category_name,
            pi.id_shop, sh.name AS shop_name, pi.status
        FROM product_instance pi
        JOIN product_type pt ON pi.id_type = pt.id_type
        JOIN product_category pc ON pt.id_category = pc.id_category
        JOIN shop sh ON pi.id_shop = sh.id_shop
        WHERE pi.status = 'in_assembly'
    """),
    ("view_brigades_for_product", """
        SELECT DISTINCT pi.serial_number, b.id_brigade, b.name AS brigade_name,
            sec.id_section, sec.name AS section_name, e.id_employee, e.last_name,
            e.first_name, e.middle_name, w.profession, w.rank
        FROM product_instance pi
        JOIN work_execution we ON we.serial_number = pi.serial_number
        JOIN work_step ws ON we.id_step = ws.id_step
        JOIN section_work_list swl ON ws.id_work = swl.id_work
        JOIN section sec ON swl.id_section = sec.id_section
        JOIN brigade b ON b.id_section = sec.id_section
        JOIN worker w ON w.id_brigade = b.id_brigade
        JOIN employee e ON w.id_employee = e.id_employee
    """),
    ("view_labs_for_product", """
        SELECT DISTINCT pi.serial_number, l.id_lab, l.name AS lab_name, l.type AS lab_type
        FROM product_instance pi
        JOIN test_execution te ON te.serial_number = pi.serial_number
        JOIN test_step ts ON te.id_test_step = ts.id_step
        JOIN test_work_list twl ON ts.id_test_work = twl.id_test_work
        JOIN equipment eq ON twl.id_equipment = eq.id_equipment
        JOIN laboratory l ON eq.id_lab = l.id_lab
    """),
    ("view_tested_products", """
        SELECT DISTINCT pi.serial_number, pt.name AS product_type_name, pt.id_category, pc.name AS category_name,
            l.id_lab, l.name AS lab_name, te.end_date AS test_date, te.result AS test_result
        FROM product_instance pi
        JOIN product_type pt ON pi.id_type = pt.id_type
        JOIN product_category pc ON pt.id_category = pc.id_category
        JOIN test_execution te ON te.serial_number = pi.serial_number
        JOIN test_step ts ON te.id_test_step = ts.id_step
        JOIN test_work_list twl ON ts.id_test_work = twl.id_test_work
        JOIN equipment eq ON twl.id_equipment = eq.id_equipment
        JOIN laboratory l ON eq.id_lab = l.id_lab
        WHERE te.result = 'passed'
    """),
    ("view_testers", """
        SELECT DISTINCT e.id_employee AS id_tester, e.last_name, e.first_name, e.middle_name,
            t.specialization, eq.id_lab, lab.name AS lab_name, pi.serial_number,
            pt.id_category, pc.name AS category_name, te.end_date AS test_date
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
        JOIN product_category pc ON pt.id_category = pc.id_category
    """),
    ("view_equipment_for_tests", """
        SELECT DISTINCT pi.serial_number, eq.id_equipment, eq.name AS equipment_name,
            eq.model AS equipment_model, l.id_lab, l.name AS lab_name
        FROM product_instance pi
        JOIN test_execution te ON te.serial_number = pi.serial_number
        JOIN test_step ts ON te.id_test_step = ts.id_step
        JOIN test_work_list twl ON ts.id_test_work = twl.id_test_work
        JOIN equipment eq ON twl.id_equipment = eq.id_equipment
        JOIN laboratory l ON eq.id_lab = l.id_lab
    """),
    ("view_products_in_assembly_summary", """
        SELECT pi.id_shop, sh.name AS shop_name, sec.id_section, sec.name AS section_name,
            pt.id_category, pc.name AS category_name, COUNT(*) AS product_count
        FROM product_instance pi
        JOIN product_type pt ON pi.id_type = pt.id_type
        JOIN product_category pc ON pt.id_category = pc.id_category
        JOIN shop sh ON pi.id_shop = sh.id_shop
        LEFT JOIN work_execution we ON we.serial_number = pi.serial_number
        LEFT JOIN work_step ws ON we.id_step = ws.id_step
        LEFT JOIN section_work_list swl ON ws.id_work = swl.id_work
        LEFT JOIN section sec ON swl.id_section = sec.id_section
        WHERE pi.status = 'in_assembly'
        GROUP BY pi.id_shop, sh.name, sec.id_section, sec.name, pt.id_category, pc.name
    """),
]

for name, sql in views:
    cur.execute(f"DROP VIEW IF EXISTS {name} CASCADE")
    cur.execute(f"CREATE VIEW {name} AS {sql}")
    print(f"OK: view {name} created")

# ============================================================
# 2. Triggers
# ============================================================

# Drop existing triggers first
trigger_names = [
    'trg_check_status_transition',
    'trg_check_foreman',
    'trg_auto_to_testing',
    'trg_unique_foreman',
    'trg_prevent_tk_delete',
]

for tname in trigger_names:
    cur.execute(f"DROP TRIGGER IF EXISTS {tname} ON product_instance")
    cur.execute(f"DROP TRIGGER IF EXISTS {tname} ON brigade")
    cur.execute(f"DROP TRIGGER IF EXISTS {tname} ON work_execution")
    cur.execute(f"DROP TRIGGER IF EXISTS {tname} ON worker")
    cur.execute(f"DROP TRIGGER IF EXISTS {tname} ON tech_card")

# Drop functions
cur.execute("""
    DROP FUNCTION IF EXISTS check_status_transition() CASCADE;
    DROP FUNCTION IF EXISTS check_foreman() CASCADE;
    DROP FUNCTION IF EXISTS auto_to_testing() CASCADE;
    DROP FUNCTION IF EXISTS unique_foreman_per_brigade() CASCADE;
    DROP FUNCTION IF EXISTS prevent_tk_delete() CASCADE;
""")

# Function 1: check_status_transition
cur.execute("""
    CREATE OR REPLACE FUNCTION check_status_transition()
    RETURNS TRIGGER AS $$
    BEGIN
        IF OLD.status = 'in_assembly' AND NEW.status NOT IN ('under_test', 'in_assembly') THEN
            RAISE EXCEPTION 'Product can only move from in_assembly to under_test';
        END IF;
        IF OLD.status = 'under_test' AND NEW.status NOT IN ('ready', 'under_test') THEN
            RAISE EXCEPTION 'Product can only move from under_test to ready';
        END IF;
        IF OLD.status = 'ready' AND NEW.status != 'ready' THEN
            RAISE EXCEPTION 'Ready product cannot change status';
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
""")

cur.execute("""
    CREATE TRIGGER trg_check_status_transition
        BEFORE UPDATE OF status ON product_instance
        FOR EACH ROW EXECUTE FUNCTION check_status_transition();
""")
print("OK: trg_check_status_transition")

# Function 2: check_foreman
cur.execute("""
    CREATE OR REPLACE FUNCTION check_foreman()
    RETURNS TRIGGER AS $$
    BEGIN
        IF NEW.id_foreman IS NOT NULL THEN
            IF NOT EXISTS (
                SELECT 1 FROM worker
                WHERE id_employee = NEW.id_foreman
                  AND id_brigade = NEW.id_brigade
                  AND is_foreman = TRUE
            ) THEN
                RAISE EXCEPTION 'Foreman must be a worker of this brigade and have is_foreman = TRUE';
            END IF;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
""")

cur.execute("""
    CREATE TRIGGER trg_check_foreman
        BEFORE INSERT OR UPDATE OF id_foreman, id_brigade ON brigade
        FOR EACH ROW EXECUTE FUNCTION check_foreman();
""")
print("OK: trg_check_foreman")

# Function 3: auto_to_testing
cur.execute("""
    CREATE OR REPLACE FUNCTION auto_to_testing()
    RETURNS TRIGGER AS $$
    DECLARE
        v_status VARCHAR(20);
        all_completed BOOLEAN;
    BEGIN
        IF NEW.status = 'completed' THEN
            SELECT status INTO v_status FROM product_instance WHERE serial_number = NEW.serial_number;
            IF v_status = 'in_assembly' THEN
                SELECT NOT EXISTS (
                    SELECT 1
                    FROM work_step ws
                    JOIN tech_card tc ON ws.id_card = tc.id_card
                    JOIN product_instance p ON p.id_type = tc.id_type
                    LEFT JOIN work_execution we ON we.serial_number = p.serial_number AND we.id_step = ws.id_step
                    WHERE p.serial_number = NEW.serial_number
                      AND (we.status IS NULL OR we.status != 'completed')
                ) INTO all_completed;
                IF all_completed THEN
                    UPDATE product_instance SET status = 'under_test' WHERE serial_number = NEW.serial_number;
                END IF;
            END IF;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
""")

cur.execute("""
    CREATE TRIGGER trg_auto_to_testing
        AFTER UPDATE OF status ON work_execution
        FOR EACH ROW EXECUTE FUNCTION auto_to_testing();
""")
print("OK: trg_auto_to_testing")

# Function 4: unique_foreman_per_brigade
cur.execute("""
    CREATE OR REPLACE FUNCTION unique_foreman_per_brigade()
    RETURNS TRIGGER AS $$
    BEGIN
        IF NEW.is_foreman = TRUE THEN
            IF EXISTS (
                SELECT 1 FROM worker
                WHERE id_brigade = NEW.id_brigade
                  AND is_foreman = TRUE
                  AND id_employee != NEW.id_employee
            ) THEN
                RAISE EXCEPTION 'Brigade already has a foreman';
            END IF;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
""")

cur.execute("""
    CREATE TRIGGER trg_unique_foreman
        BEFORE INSERT OR UPDATE OF is_foreman, id_brigade ON worker
        FOR EACH ROW EXECUTE FUNCTION unique_foreman_per_brigade();
""")
print("OK: trg_unique_foreman")

# Function 5: prevent_tk_delete
cur.execute("""
    CREATE OR REPLACE FUNCTION prevent_tk_delete()
    RETURNS TRIGGER AS $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM product_instance
            WHERE id_type = OLD.id_type
              AND status != 'ready'
        ) THEN
            RAISE EXCEPTION 'Cannot delete tech card: unfinished products of this type exist';
        END IF;
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
""")

cur.execute("""
    CREATE TRIGGER trg_prevent_tk_delete
        BEFORE DELETE ON tech_card
        FOR EACH ROW EXECUTE FUNCTION prevent_tk_delete();
""")
print("OK: trg_prevent_tk_delete")

conn.commit()
print("\n=== ALL DONE ===")

# Verify
cur.execute("SELECT tgname FROM pg_trigger WHERE tgname LIKE 'trg_%' ORDER BY tgname")
print("Triggers:", [r[0] for r in cur.fetchall()])

cur.execute("SELECT COUNT(*) FROM view_testers")
print("view_testers count:", cur.fetchone()[0])

cur.close()
conn.close()
