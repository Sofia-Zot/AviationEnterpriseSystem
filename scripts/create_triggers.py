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

# Drop existing triggers first
trigger_names = [
    'trg_check_status_transition',
    'trg_check_foreman',
    'trg_auto_to_testing',
    'trg_unique_foreman',
    'trg_prevent_tk_delete',
]
for tname in trigger_names:
    for table in ['product_instance', 'brigade', 'work_execution', 'worker', 'tech_card']:
        cur.execute(f"DROP TRIGGER IF EXISTS {tname} ON {table}")

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
print("All triggers created")

cur.execute("SELECT tgname FROM pg_trigger WHERE tgname LIKE 'trg_%' ORDER BY tgname")
print("Triggers:", [r[0] for r in cur.fetchall()])

cur.close()
conn.close()
