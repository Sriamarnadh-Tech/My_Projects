import sqlite3
con = sqlite3.connect('traffic.db')
cur = con.cursor()
cur.execute("PRAGMA table_info('challans')")
cols = cur.fetchall()
print('challans columns:')
for c in cols:
    print(c)
con.close()
