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

# Получаем список всех пользовательских таблиц
cur.execute('''
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    ORDER BY table_name
''')
tables = [row[0] for row in cur.fetchall()]

for table in tables:
    print(f'\n=== TABLE: {table} ===')
    
    # Получаем колонки
    cur.execute('''
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position
    ''', (table,))
    
    columns = cur.fetchall()
    for col in columns:
        col_name, data_type, nullable, default = col
        print(f'  {col_name}: {data_type}', end='')
        if nullable == 'NO':
            print(' NOT NULL', end='')
        if default:
            print(f' DEFAULT {default}', end='')
        print()
    
    # Получаем внешние ключи
    cur.execute('''
        SELECT
            kcu.column_name,
            ccu.table_name AS foreign_table,
            ccu.column_name AS foreign_column,
            tc.constraint_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = %s
    ''', (table,))
    
    fks = cur.fetchall()
    if fks:
        print('  FK:')
        for fk in fks:
            col_name, fk_table, fk_col, cons_name = fk
            print(f'    {col_name} -> {fk_table}({fk_col})')
    
    # Получаем первичный ключ
    cur.execute('''
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
        WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_name = %s
    ''', (table,))
    
    pks = cur.fetchall()
    if pks:
        pk_cols = ', '.join([pk[0] for pk in pks])
        print(f'  PK: {pk_cols}')

cur.close()
conn.close()
