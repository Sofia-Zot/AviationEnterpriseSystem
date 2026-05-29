-- Добавляем колонку id_manager (FK на engineer.id_employee)
ALTER TABLE section 
ADD COLUMN IF NOT EXISTS id_manager INT 
REFERENCES engineer(id_employee) 
ON DELETE SET NULL 
ON UPDATE CASCADE;

-- Добавляем уникальный индекс (один менеджер на участок)
CREATE UNIQUE INDEX IF NOT EXISTS idx_section_manager 
ON section(id_manager) 
WHERE id_manager IS NOT NULL;

-- Назначаем начальников участков (выбираем первых инженеров из каждого цеха)
-- Участок 1 (Assembly Line 1, Shop 1) -> Engineer 201 (Chief Engineer)
UPDATE section SET id_manager = 201 WHERE id_section = 1;

-- Участок 2 (Welding Shop, Shop 1) -> Engineer 202 (Senior Engineer)
UPDATE section SET id_manager = 202 WHERE id_section = 2;

-- Участок 3 (Engine Test Stand, Shop 2) -> Engineer 203 (Chief Technologist)
UPDATE section SET id_manager = 203 WHERE id_section = 3;

-- Участок 4 (Engine Assembly, Shop 2) -> Engineer 204 (Technologist)
UPDATE section SET id_manager = 204 WHERE id_section = 4;

-- Участок 5 (Component Machining, Shop 3) -> Engineer 205 (Design Engineer)
UPDATE section SET id_manager = 205 WHERE id_section = 5;

-- Участок 6 (Electronics Assembly, Shop 3) -> Engineer 206 (Senior Technician)
UPDATE section SET id_manager = 206 WHERE id_section = 6;

-- Участок 7 (Final Inspection, Shop 4) -> Engineer 207 (Master)
UPDATE section SET id_manager = 207 WHERE id_section = 7;

-- Участок 8 (Quality Control, Shop 5) -> Engineer 201 (Chief Engineer)
UPDATE section SET id_manager = 201 WHERE id_section = 8;

-- Пересоздаём view_sections_with_managers (если существует)
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
'Участки цехов и их начальники (через section.id_manager -> engineer). Фильтрация в клиенте: WHERE id_shop = N.';

