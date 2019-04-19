import sqlite3

conn = sqlite3.connect('portfolio.db')

c = conn.cursor()

c.execute("""CREATE TABLE users {
	""")