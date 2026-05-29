from db.connection import DatabaseConnection

db = DatabaseConnection()
conn = db.get_connection()
try:
    with conn.cursor() as cur:
        for table in ['test_card', 'test_work_list', 'work_step']:
            print('=== ' + table + ' ===')
            cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s", (table,))
            for row in cur.fetchall():
                print('  ' + row[0] + ': ' + row[1])
            print()
finally:
    db.return_connection(conn)
