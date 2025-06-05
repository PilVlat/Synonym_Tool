import sqlite3
from google_ngram_downloader import readline_google_store


conn = sqlite3.connect('database_2008_copy.db')
conn_target = sqlite3.connect('cleandb.db')

cursor = conn.cursor()
cursor_target = conn_target.cursor()
'''cursor.execute("DROP TABLE best_one_v2")
cursor.execute("CREATE TABLE best_one_v2 (word TEXT PRIMARY KEY, year INTEGER, match_count INTEGER, volume_count INTEGER)")
cursor.execute("""SELECT word, year, match_count, volume_count FROM best_one_v1 WHERE match_count>10000
""")'''


'''delete_query = """
    DELETE FROM merged_word_data
    WHERE word LIKE '%;%'
       OR word LIKE '%:%'
       OR word LIKE '%.%'
       OR word LIKE '%-%'
       OR word LIKE '%\\_%' ESCAPE '\\'
       OR word LIKE '%$%'
       OR word LIKE '%=%'
       OR word LIKE '%{%'
       OR word LIKE '%}%'
       OR word LIKE '%]%'
       OR word LIKE '%[%'
       OR word LIKE '%(%'
       OR word LIKE '%)%'
       OR word LIKE '%`%'
       OR word LIKE '%\\%'
       OR word LIKE '%\\%%' ESCAPE '\\'
       OR word LIKE '%^%'
       OR word LIKE '%&%'
       OR word LIKE '%+%'
       OR match_count<1000;
"""'''
cursor.execute("SELECT * FROM merged_word_data")
rows = cursor.fetchall()
print(rows)
cursor_target.execute("CREATE TABLE ngram1_filtered (word TEXT PRIMARY KEY, year INTEGER, match_count INTEGER, volume_count INTEGER)")
cursor_target.executemany(f"INSERT INTO ngram1_filtered VALUES (?,?,?,?)", rows)



conn_target.commit()
cursor_target.close()
conn.commit()
cursor.close()
conn.close()


print("Done successfully!")
