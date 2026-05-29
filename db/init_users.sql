-- Удалить существующую таблицу (если есть)
DROP TABLE IF EXISTS users CASCADE;

-- Создать таблицу пользователей
CREATE TABLE users (
    login VARCHAR(50) PRIMARY KEY,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    id_employee INT REFERENCES employee(id_employee) ON DELETE SET NULL
);

-- Создать комментарии к таблице
COMMENT ON TABLE users IS 'Таблица пользователей системы для аутентификации';
COMMENT ON COLUMN users.login IS 'Логин пользователя (уникальный)';
COMMENT ON COLUMN users.password_hash IS 'Хеш пароля (bcrypt)';
COMMENT ON COLUMN users.role IS 'Роль пользователя (admin, hr_manager, master, foreman, tester, technologist, analyst)';
COMMENT ON COLUMN users.id_employee IS 'Ссылка на сотрудника (опционально)';

-- Вставить начальных пользователей
-- Пароли сгенерированы через bcrypt (rounds=12)
INSERT INTO users (login, password_hash, role, id_employee) VALUES
    ('admin', '$2b$12$3W3MYvlnGAKzwQCYIbewA.DPQZaJkXmgWxahiCAlF5XNgCVBVB9DK', 'admin', NULL),
    ('hr_user', '$2b$12$EQ/1gqvaWE65QjOuUJxkLu4mWRlO2wmOef7RrJJJ9bIDL8vW5OyRu', 'hr_manager', NULL),
    ('master1', '$2b$12$qZIXNKTW3IgNmPV6eML73.AYxXMgzRB.QYzHd0MT4QqnbuwScJHnS', 'master', NULL),
    ('brigadier1', '$2b$12$eYNErEjOsmlUEM2gphG6oeiZvLBfFdbHk4C2q4d3DeND6MBihQJx6', 'foreman', NULL),
    ('tester1', '$2b$12$M42ooEqIKhyZabimGRUjJuqMZl5DbRx9y81yQ49.hblNZcayCmvOK', 'tester', NULL),
    ('technologist1', '$2b$12$obsqPZfGl3RgO4wvT9G3e.GaizXv6LGq6BMMxIVKwkxvs5YS1XiDi', 'technologist', NULL),
    ('analyst1', '$2b$12$8/IdB0/O.BJ5zGnEJkRNTuiHgu/22Y5CP9DtOmHaF4jSzbutmTPZ6', 'analyst', NULL);

-- Комментарий к данным
COMMENT ON TABLE users IS 'Пользователи: admin (admin123), hr_user (hr123), master1 (master123), brigadier1 (brig123), tester1 (test123), technologist1 (tech123), analyst1 (an1234)';

-- Инструкция по применению:
-- 1. Выполнить: psql -U postgres -d aircraft_db -f db/init_users.sql
-- 2. Либо запустить из Python после подключения к БД