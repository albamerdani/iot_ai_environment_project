import serial
import sys
import time
import datetime
import RPi.GPIO as GPIO
import sqlite3
import urllib
import Adafruit_BMP.BMP085 as BMP085
import Adafruit_DHT
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Krijo nje 'objekt' qe permban te dhena BMP180
sensor = BMP085.BMP085()

#Vendos komunikimin serial me ane te portes USB si paisje e jashtme per sensorin e pluhurit
ser = serial.Serial('/dev/ttyUSB0')

#numri i Pinit per buzzer alarm,freskuesen dhe per pinin e te dhenave te sensorit te temperatures
buzzerPin = 16
tempPin=18
fanPin = 8
fanMinSpeed = 25
PWM_FREQ = 25
GPIO.setwarnings(False)

#Menyra e numerimit te pineve
GPIO.setmode(GPIO.BOARD)

#Percaktimi i pinit te alarmit si output
GPIO.setup(buzzerPin, GPIO.OUT)

#Percaktimi i pinit te sensorit te temperatures si input dhe freskueses si output
GPIO.setup(tempPin, GPIO.IN)
GPIO.setup(fanPin, GPIO.OUT)
fan = GPIO.PWM(fanPin, PWM_FREQ)
fan.start(0)

x = 0
alarm = 0 #False

# Vendos write API key
myAPI = '88510QA7PG91TXE0' 
# URL ku do dergohen te dhenat
baseURL = 'https://api.thingspeak.com/update?api_key=%s' % myAPI

#funksion qe ndez freskuesen nese temperatura eshte mbi nje vlere te caktuar
def freskuese(temp):
    if temp > 25:
        fan.ChangeDutyCycle(25)
        print("Freskuesja hapur!")
    else:
        fan.ChangeDutyCycle(0)
        print("Freskuesja mbyllur!")
        fan.stop()

#funksion qe dergon vlerat e parametrave mjedisore ne Cloud
def sendData_Cloud(pm2_5, pm10, temp, trysnia, alarm):
    # Dergoj te dhenat te platforma Cloud
    connThings = urllib.request.urlopen(baseURL + '&field1=%s&field2=%s&field3=%s&field4=%s&field5=%s' % (pm2_5, pm10, temp, trysnia, alarm))
    print (connThings.read())
    # Mbyll lidhjen
    connThings.close()


def krijo_tabele():
    try:
        # metoda kthen objektin SQLite Connection
        conn = sqlite3.connect('mjedisi.db')
        # objekti cursor na lejon te ekzekutojme komanda ose query SQLite me ane te Python
        cursor = conn.cursor()
        print("Lidhja me databazen u vendos")

        cursor.execute("CREATE TABLE IF NOT EXISTS 'parametrat_ajri' ( `id` INTEGER PRIMARY KEY AUTOINCREMENT, `data_ora` DATETIME NOT NULL, `pluhuri2_5` NUMERIC NOT NULL, `pluhuri10` NUMERIC NOT NULL, `temperatura` NUMERIC NOT NULL, `lageshtira` NUMERIC NOT NULL, `trysnia` NUMERIC NOT NULL, `alarm_status` INTEGER NOT NULL, `gjatesia_gjeo` NUMERIC NULL, `gjeresia_gjeo` NUMERIC NULL, 'gazi' NUMERIC NULL, 'ndricimi' NUMERIC NULL, 'niveli_zhurmes' NUMERIC NULL,)")

        conn.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("Error!!")
    finally:
        if(conn):
            conn.close()
            print("Lidhja me sqlite u mbyll")


krijo_tabele()


def lexo_rekord():
    try: 
        # metoda kthen objektin SQLite Connection
        conn = sqlite3.connect('mjedisi.db')
        # objekti cursor na lejon te ekzekutojme komanda ose query SQLite me ane te Python
        cursor = conn.cursor()
        print("Lidhja me databazen u vendos")

        query = """SELECT * FROM 'perdoruesi' WHERE 'perdoruesi'.id = 1"""
        cursor.execute(query)
        rows = cursor.fatchall()
        cursor.close()
    except sqlite3.Error as error:
        print("Error gjate kohes se kerkimit!")
    finally:
        if(conn):
            conn.close()
            print("Lidhja me sqlite u mbyll")
    return rows

        
def shto_matje(koha, pm2_5, pm10, temp, lag, trysnia, alarm):
    try:
        # metoda kthen objektin SQLite Connection
        conn = sqlite3.connect('mjedisi.db')
        # objekti cursor na lejon te ekzekutojme komanda ose query SQLite me ane te Python
        cursor = conn.cursor()
        print("Lidhja me databazen u vendos")

        query = """INSERT INTO 'parametrat_ajri' (id, data_ora, pluhuri2_5, pluhuri10, temperatura, lageshtira, trysnia, alarm_status, gjatesia_gjeo, gjeresia_gjeo, gazi, ndricimi, niveli_zhurmes) VALUES ('',?,?,?,?,?,?,?,'','','','','')"""
        cursor.execute(query,(koha, pm2_5, pm10, temp, lag, trysnia, alarm))
        conn.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("Error gjate kohes se shtimit te matjes!")
    finally:
        if(conn):
            conn.close()
            print("Lidhja me sqlite u mbyll")


def ruaj_matje_file(koha, pm2_5, pm10, temp, trysni, alarm_status):
    with open("parametra_ajri.csv", 'a') as log:
        log.write("{0},{1},{2},{3},{4},{5}\n".format(koha,str(pm2_5),str(pm10),str(temp),str(trysni),str(alarm_status)))


#funksion qe dergon nje njoftim, email nga RPi te perdoruesi 
def dergo_njoftim():
    rows = lexo_rekord()
    for row in rows:
        username = row[1]
        password = row[2]


    USERNAME = "perdoruesiot@gmail.com" #"username@gmail.com"
    PASSWORD = "user.iot" #"password"
    MAILTO  = albamerdani.am@gmail.com #"mailto@gmail.com"

    msg = MIMEText('Alarmi eshte ndezur. Parametrat e mjedisit jane jo normale.')
    msg['Subject'] = 'Njoftim IoT'
    msg['From'] = USERNAME
    msg['To'] = MAILTO

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo_or_helo_if_needed()
    server.starttls()
    server.ehlo_or_helo_if_needed()
    server.login(USERNAME,PASSWORD)
    server.sendmail(USERNAME, MAILTO, msg.as_string())
    server.quit()


  #cikli ekzekutimit  
while x < 1000:
    data = []
    for index in range(0,10):
        datum = ser.read()
        data.append(datum)

    koha = datetime.datetime.now()
    pm2_5 = int.from_bytes(b''.join(data[2:4]), byteorder = 'little')/10
    pm10 = int.from_bytes(b''.join(data[4:6]), byteorder = 'little')/10

    temp = sensor.read_temperature()
    trysnia = sensor.read_pressure()

    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, tempPin)

    print("Data dhe ora:" + str(koha))
    print("PM 2.5: " + str(pm2_5))
    print("PM 10: " + str(pm10))
    print('Lageshtira = ', humidity)
    print ('Temperatura = {0:0.2f} *C'.format(temp)) # Temperatura ne Celcius
    print ('Trysnia = {0:0.2f} Pa'.format(trysnia)) # Trysnia
    print ('Lartesia = {0:0.2f} m'.format(sensor.read_altitude())) # Lartesia aktuale
    print ('Trysnia ne nivelin e detit = {0:0.2f} Pa'.format(sensor.read_sealevel_pressure())) # Trysnia niveli detit

    freskuese(temp)
    
    if pm2_5 > 14 or pm10 > 25 or temp > 25 or temp < 18:
        GPIO.output(buzzerPin, GPIO.HIGH)       #gjenero alarm nese ndotja e ajrit 
        alarm = 1 #True
        dergo_njoftim()
        print('Alarm!! Beep!')                  #eshte mbi normen qe ti vendos
        time.sleep(2)                          # beeps per 2 sekonda
        GPIO.output(buzzerPin, GPIO.LOW)
        time.sleep(1)                           # heshtje per 1 sekonde
    else:
        GPIO.output(buzzerPin, GPIO.LOW)
        alarm = 0
        print('No alarm')

    sendData_Cloud(pm2_5, pm10, temp, lag, trysnia, alarm)
    shto_matje(koha, pm2_5, pm10, temp, lag, trysnia, alarm)
    ruaj_matje_file(koha, pm2_5, pm10, temp, lag, trysnia, alarm)

     x = x + 1
    print('')
    time.sleep(15)


#importoj librarite e nevojshme per vizualizimin grafik ne lidhje me te dhenat
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import pyplot, dates
from csv import reader
from dateutil import parser
from numpy import genfromtxt
from datetime import datetime as dt


dateconv = lambda s:dt.strptime(s, "%Y/%m/%d %H:%M:%S.%f")
col_names = ["field3", "field5"]
fig = plt.figure()
ax = fig.add_subplot(1,1,1)


def animateTemp_Alarm():
    with open("/home/pi/Downloads/parametrat_ajri.csv", 'r') as f:
       data = list(reader(f))
    temp = [i[4] for i in data[1:100]]
    alarmi = [i[6] for i in data[1:100]]
    #time = [parser.parse(i[0] for i in data[1:100])]
    #data = pd.read_csv("parametra_ajri.csv", names = col_names)
    #mydata = genfromtxt("parametra_ajri.csv", delimiter=',', names = col_names)
    #mydata['Data'] = {"mydata['Data']":dateconv}

    x = alarmi #data['alarm']
    y = temp #data['Temp']
    plt.plot(x,y)

    ax.plot(x, y)
    plt.subplots_adjust(bottom=0.30)
    plt.title('Temperatura-Alarmi Graph')
    plt.ylabel('Temp (deg C)')
    plt.xlabel('Alarmi')
    plt.show()


def animatePM_Alarm():
    with open("/home/pi/Downloads/parametrat_ajri.csv", 'r') as f:
       data = list(reader(f))
    pm = [i[3] for i in data[1:100]]
    alarmi = [i[6] for i in data[1:100]]
    #time = [parser.parse(i[0] for i in data[1:100])]
    #data = pd.read_csv("parametra_ajri.csv", names = col_names)
    #mydata = genfromtxt("parametra_ajri.csv", delimiter=',', names = col_names)
    #mydata['Data'] = {"mydata['Data']":dateconv}

    x = pm #data['PM10']
    y = alarmi #data['alarm']
    plt.bar(x,y, color = colors)
    plt.subplots_adjust(bottom=0.30)
    plt.title('Pluhuri-Alarmi Graph')
    plt.ylabel('PM 10')
    plt.xlabel('Alarmi')
    plt.show()

animatePM_Alarm()
animateTemp_Alarm()

#ani=animation.FuncAnimation(fig, animate, interval=1000*60)

GPIO.cleanup()
sys.exit(1)
