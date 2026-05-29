from db.connection import DatabaseConnection

db = DatabaseConnection()
conn = db.get_connection()
try:
    with conn.cursor() as cur:
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
        print('All tables:')
        for row in cur.fetchall():
            print('  ' + row[0])
finally:
    db.return_connection(conn)
