import pymysql
import serial
import datetime
from datetime import timedelta
import os
import time

# tijd instellen
os.system("ntpdate ntp.ubuntu.com")

# seriele verbinding
ser=serial.Serial('/dev/ttyACM0', 115200)

# Een integer sturen naar Arduino
def sendInt(data):
	ser.write(chr(data))
	print ser.readline()
	return

#Een char sturen naar Arduino
def sendChar(data):
	ser.write(data)
	print ser.readline()
	return

#Check screen initialized
ser.readline()

mededelingp1 = 0; #pointer naar waar we zitten in de mededeligen database
eventp1 = 0; # pointer naar event db

# Lus die herhaalt word om de schermen te verversen
while True:
	cn=pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='',db='ASRO') # connecteren met de databank
	cur = cn.cursor() # databank cursor
	now = datetime.datetime.now() # tijd ophalen
	dag = "" # Welke dag zijn we vandaag?
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
	status = "" # Open - Gesloten - Zo Terug
	cur.execute("SELECT status FROM pauze") # Zo Terug?
	r3 = cur.fetchall()
	if (r3[0][0] == 0):
		cur.execute("SELECT openu, openm, geslotenu, geslotenm FROM openingstijden WHERE dag = \""+dag+"\"")
		r3 = cur.fetchall()
		print r3
		print now.hour
		if (r3[0][0] < now.hour and r3[0][2] > now.hour):
			status = "OPEN"
		elif (r3[0][0] == now.hour and r3[0][1] < now.minute):
			status = "OPEN"
		elif (r3[0][2] == now.hour and r3[0][3] > now.minute):
			status = "OPEN"
		else:
			status = "GESLOTEN"
	else:
		status = "ZO TERUG"
	month = "" # welke maand is het?
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
	datum = dag + " " + str(now.day) + " " + month # Datum string instellen
	mededeling = "" # Mededelingen instellen
	for i in range(0,2):
		cur.execute("SELECT id, content FROM mededelingen WHERE id > " + str(mededelingp1)) #mededelingen ophalen die na onze pointer komen
		r3 = cur.fetchall() # bovenste van de stack halen
		if r3:
			mededelingp1 = r3[0][0] # pointer updaten
			mededeling = r3[0][1]
			break # mededeling is ingesteld - uit lus gaan
		else:
			mededelingp1 = 0 # pointer resetten en lus nog eenmaal uitvoeren
	event_title = ""
	event_date = ""
	event_begin = ""
	event_end = ""
	event_text = ""
	for i in range(0,2):
		cur.execute("SELECT id, m, d, y, start_time, end_time, title, text FROM pec_mssgs WHERE m >= " + str(now.month) + " AND y >= " + str(now.year) + " ORDER BY y, m, d")
		p1 = 1;
		for r3 in cur.fetchall():
			td = datetime.datetime(r3[3], r3[1], r3[2], 0, 0, 0)
			if ((td - now) < timedelta(days = 30)): # is event binnen 30 dagen
				if ((td - now) > timedelta(days = -1)):
					if (p1 > eventp1): # niet 2 x zelfde event laten zien
						event_title = r3[6]
						event_text = r3[7]
						event_date = str(r3[2]) + "/" + str(r3[1])
						if (str(r3[4]) != "2 days, 7:55:55"): # geen begin ingesteld
							event_begin = str(r3[4])
							event_begin = event_begin[:-3]
						else:
							event_begin = "onbekend"
						if (str(r3[5]) != "2 days, 7:55:55"): # geen eind ingesteld
							event_end = str(r3[5])
							event_end = event_end[:-3]
						else:
							event_end = "onbekend"
						eventp1 = p1
						break
					else:
						p1 += 1
				else:
					p1 += 1
			else:
				eventp1 = 0;
				break
		if (event_title != ""):
			break
		else:
			eventp1 = 0
	print event_date
	print event_title
	print event_text
	print event_begin
	print event_end
	print status
	print datum
	print mededeling
	for i in range(0,3): # voor elke scherm
		cur.execute("SELECT layout, textbox FROM form WHERE active = " + str(i+1)) # textboxes ophalen
		sendInt(242) # 242 = we gaan een scherm selecteren
		sendInt(i+1) # nummer van het scherm doorgeven (1-3)
		r1 = cur.fetchall()
		print r1
		if r1:
			if (r1[0][1] != None):
				cur.execute("SELECT x1, y1, x2, y2, font, content FROM textbox WHERE name = \"" + r1[0][1] + "\"")
				for r2 in cur.fetchall():
					sendInt(243) # 243 = we gaan een textbox doorsturen
					sendInt(r2[4]) # stuur de font door (1: titel - 2: subtitel - 3: text)
					sendInt(r2[1]) # stuur y1 (coordinaten van link boven (x1, y1) en rechts onder (x2, y2))
					if (r2[4] == 3): # als het geen subtitel of titel is
						sendInt(r2[0]) # stuur x1
						sendInt(r2[2]) # stuur x2
						sendInt(r2[3]) # stuur y2
					content = r2[5].upper() # wat is in deze textbox?
					content = content.replace(":STATUS:", status)
					content = content.replace(":DATE:", datum)
					content = content.replace(":MEDEDELING:", mededeling)
					content = content.replace(":EVENT_TITLE:", event_title)
					content = content.replace(":EVENT_BEGIN:", event_begin)
					content = content.replace(":EVENT_END:", event_end)
					content = content.replace(":EVENT_TEXT:", event_text)
					content = content.replace(":EVENT_DATE:", event_date)
					letters = list(content) # content opsplitsen in letters
					for l in letters:
						sendChar(l)
					sendInt(244) # einde van een textbox (er komt geen tekst meer)
			if (r1[0][0] != None):
				cur.execute("SELECT x, y FROM layout WHERE name = \"" + r1[0][0] + "\"")
				sendInt(245) # 245 = pixels sturen
				for r2 in cur.fetchall():
					sendInt(r2[0])
					sendInt(r2[1])
				sendInt(244)
	cur.close()
	cn.close() # databank connection sluiten
	time.sleep(30) # wacht 30 seconden
