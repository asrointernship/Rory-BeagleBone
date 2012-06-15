import pymysql

cn=pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='',db='ASRO')


cur = cn.cursor()

cur.execute("DROP TABLE IF EXISTS form")
cur.execute("DROP TABLE IF EXISTS layout")
cur.execute("DROP TABLE IF EXISTS textbox")
cur.execute("DROP TABLE IF EXISTS openingstijden")
cur.execute("DROP TABLE IF EXISTS mededelingen")
cur.execute("DROP TABLE IF EXISTS pauze")
cur.execute("""CREATE TABLE IF NOT EXISTS layout(
			id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
			x SMALLINT NOT NULL,
			y SMALLINT NOT NULL,
			name VARCHAR(100) NOT NULL)""")
cur.execute("""CREATE TABLE IF NOT EXISTS textbox(
			id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
			x1 SMALLINT NOT NULL,
			x2 SMALLINT NOT NULL,
			y1 SMALLINT NOT NULL,
			y2 SMALLINT NOT NULL,
			name VARCHAR(100) NOT NULL,
			font SMALLINT NOT NULL,
			content TEXT)""")
cur.execute("""CREATE TABLE IF NOT EXISTS form (
			id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
			name VARCHAR(100) NOT NULL,
			layout VARCHAR(100),
			textbox VARCHAR(100),
			active SMALLINT NOT NULL)""")

cur.execute("ALTER TABLE form ADD FOREIGN KEY (layout) REFERENCES layout(name)")
cur.execute("ALTER TABLE form ADD FOREIGN KEY (textbox) REFERENCES textbox(name)")

cur.execute("""CREATE TABLE IF NOT EXISTS openingstijden(
			dag VARCHAR(10) NOT NULL PRIMARY KEY,
			openu SMALLINT NOT NULL,
			openm SMALLINT NOT NULL,
			geslotenu SMALLINT NOT NULL,
			geslotenm SMALLINT NOT NULL)""")
cur.execute("""INSERT INTO ASRO.openingstijden (dag, openu, openm, geslotenu, geslotenm) VALUES
			("Maandag", 0, 0, 0, 0),
			("Dinsdag", 0, 0, 0, 0),
			("Woensdag", 0, 0, 0, 0),
			("Donderdag", 0, 0, 0, 0),
			("Vrijdag", 0, 0, 0, 0),
			("Zaterdag", 0, 0, 0, 0),
			("Zondag", 0, 0, 0, 0);""")

cur.execute("""CREATE TABLE IF NOT EXISTS mededelingen(
			id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
			content TEXT NOT NULL)""")
cur.execute("""CREATE TABLE IF NOT EXISTS pauze(
			id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
			status BOOLEAN NOT NULL)""")
cur.execute("""INSERT INTO ASRO.pauze (status) VALUES (false)""")

cur.close()
cn.close()