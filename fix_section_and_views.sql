-- ============================================================
-- МИГРАЦИЯ: исправление таблицы section и двух представлений
-- AviationEnterpriseSystem
-- ============================================================

-- ------------------------------------------------------------
-- 1. Добавление поля id_manager в таблицу section
-- ------------------------------------------------------------
-- Проверяем, существует ли уже поле (идемпотентность)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'section' AND column_name = 'id_manager'
    ) THEN
        ALTER TABLE section
        ADD COLUMN id_manager INT
        REFERENCES engineer(id_employee)
        ON DELETE SET NULL
        ON UPDATE CASCADE;

        -- Уникальность: один инженер = один участок
        ALTER TABLE section
        ADD CONSTRAINT uq_section_manager UNIQUE (id_manager);

        RAISE NOTICE 'Поле id_manager добавлено в таблицу section';
    ELSE
        RAISE NOTICE 'Поле id_manager уже существует в таблице section';
    END IF;
END $$;


-- ------------------------------------------------------------
-- 2. Обновление существующих данных (опционально)
-- ------------------------------------------------------------
-- По умолчанию все id_manager = NULL.
-- Если нужно назначить начальников вручную, раскомментируйте
-- и укажите реальные id_employee из таблицы engineer:
--
-- UPDATE section SET id_manager = 4 WHERE id_section = 1;  -- Section Manager
-- UPDATE section SET id_manager = 15 WHERE id_section = 2; -- Section Manager
--
-- Проверка: какие инженеры имеют position = 'Section Manager':
-- SELECT e.id_employee, e.last_name, e.first_name, eng.position
-- FROM engineer eng
-- JOIN employee e ON eng.id_employee = e.id_employee
-- WHERE eng.position = 'Section Manager';


-- ------------------------------------------------------------
-- 3. Пересоздание представления: участки и начальники
-- ------------------------------------------------------------
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


-- ------------------------------------------------------------
-- 4. Пересоздание представления: завершённые изделия
-- ------------------------------------------------------------
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
