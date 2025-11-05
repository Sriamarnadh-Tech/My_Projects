import sqlite3
con = sqlite3.connect('traffic.db')
cur = con.cursor()
try:
    cur.execute("ALTER TABLE challans ADD COLUMN location VARCHAR(200)")
    con.commit()
    print('Added location column')
except Exception as e:
    print('Migration error:', e)
finally:
    con.close()
