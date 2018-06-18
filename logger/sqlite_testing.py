import sqlite3

if __name__ == '__main__':
	exists = False
	doesnt_exist = False
	conn = sqlite3.connect('June.db')
	c = conn.cursor()
	try:
		c.execute('CREATE TABLE Day1 (Hour text PRIMARY KEY, Minute text, Temp int, Humid int)')
	except sqlite3.OperationalError:
		print('db exists')
		exists = True
	try:
		c.execute("INSERT INTO Day2 VALUES('23','27',24,20)")
	except sqlite3.OperationalError:
		print('db doesnt exist')
		doesnt_exist = True

	print('handled doesnt exist: {}'.format(doesnt_exist))
	print('handled exists: {}'.format(exists))

