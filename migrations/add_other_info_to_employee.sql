-- Migration: add other_info column to employee table
-- Date: 2025-05-30
-- Description: adds other_info field for non-system employees (HR, analyst, etc.)

ALTER TABLE employee ADD COLUMN IF NOT EXISTS other_info VARCHAR(200);

COMMENT ON COLUMN employee.other_info IS
'Должность/статус для внесистемных сотрудников (HR, аналитик, технолог и т.д.).';
