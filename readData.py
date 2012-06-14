import pymysql
import serial
import datetime
import os
import time

os.system("ntpdate ntp.ubuntu.com")

ser=serial.Serial('/dev/ttyACM0', 115200)

def sendInt(data):
	#print "sending " + data
	ser.write(chr(data))
	print ser.readline()
	return

def sendChar(data):
	ser.write(data)
	print ser.readline()
	return

#Check screen initialized
ser.readline()

mededelingp1 = 0;

while True:
	cn=pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='',db='ASRO')
	cur = cn.cursor()
	now = datetime.datetime.now()
	dag = ""
	if (now.weekday() == 0):
		dag = "Maandag"
	elif (now.weekday() == 1):
		dag = "Dinsdag"
	elif (now.weekday() == 2):
		dag = "Woensdag"
	elif (now.weekday() == 3):
		dag = "Donderdag"
	elif (now.weekday() == 4):
		dag = "Vrijdag"
	elif (now.weekday() == 5):
		dag = "Zaterdag"
	else:
		dag = "Zondag"
	status = ""
	cur.execute("SELECT status FROM pauze")
	r3 = cur.fetchall()
	if (r3[0][0] == 0):
		cur.execute("SELECT openu, openm, geslotenu, geslotenm FROM openingstijden WHERE dag = \""+dag+"\"")
		r3 = cur.fetchall()
		print r3
		print now.hour
		if (r3[0][0] < now.hour & r3[0][2] > now.hour):
			status = "OPEN"
		elif (r3[0][0] == now.hour & r3[0][1] < now.minute):
			status = "OPEN"
		elif (r3[0][2] == now.hour & r3[0][3] > now.minute):
			status = "OPEN"
		else:
			status = "GESLOTEN"
	else:
		status = "ZO TERUG"
	month = ""
	if (now.month == 1):
		month = "Januari"
	elif (now.month == 2):
		month = "Februari"
	elif (now.month == 3):
		month = "Maart"
	elif (now.month == 4):
		month = "April"
	elif (now.month == 5):
		month = "Mei"
	elif (now.month == 6):
		month = "Juni"
	elif (now.month == 7):
		month = "Juli"
	elif (now.month == 8):
		month = "Augustus"
	elif (now.month == 9):
		month = "September"
	elif (now.month == 10):
		month = "October"
	elif (now.month == 11):
		month = "November"
	elif (now.month == 12):
		month = "December"
	datum = dag + " " + str(now.day) + " " + month
	mededeling = ""
	for i in range(0,1):
		cur.execute("SELECT id, content FROM mededelingen WHERE id >= " + str(mededelingp1))
		r3 = cur.fetchall()
		if r3:
			mededelingp1 = r3[0][0]
			mededeling = r3[0][1]
		else:
			mededelingp1 = 0
	print status
	print datum
	print mededeling
	cur.execute("SELECT layout, textbox FROM form WHERE active = true")
	r1 = cur.fetchall()
	if r1:
		if (r1[0][1] != None):
			sendInt(241)
			cur.execute("SELECT x1, y1, x2, y2, font, content FROM textbox WHERE name = \"" + r1[0][1] + "\"")
			for r2 in cur.fetchall():
				sendInt(243)
				sendInt(r2[4])
				sendInt(r2[1])
				if (r2[4] == 3):
					sendInt(r2[0])
					sendInt(r2[2])
					sendInt(r2[3])
				content = r2[5].upper()
				content = content.replace(":STATUS:", status)
				content = content.replace(":DATE:", datum)
				content = content.replace(":MEDEDELING:", mededeling)
				letters = list(content)
				for l in letters:
					sendChar(l)
				sendInt(244)
	cur.close()
	cn.close()
	time.sleep(5)
