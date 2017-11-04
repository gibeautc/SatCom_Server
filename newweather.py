#!/usr/bin/env python
import time
import sys
import json
import logging
import MySQLdb
import urllib
import datetime

db=MySQLdb.connect('localhost','root','aq12ws','weather')
curs=db.cursor()
key=["35859b32434c5985","803ee257021d3c0e"]
kindex=0

#update times (min)
UT_FORECAST=120
UT_CURRENT=30
UT_ALERT=180
#types
FORECAST=0x01
CURRENT=0x02
ALERT=0x03

import MySQLdb 
TEST=False

import logging as log
log.basicConfig(filename='/home/pi/log/weather.log',level=logging.DEBUG,format='%(asctime)s %(levelname)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


def parse_forecast(data,location):
	#data=json.loads(data)
	log.info("Adding Forecast for "+location)
	hourly=data['hourly_forecast']
	for e in hourly:
		day=e['FCTTIME']['mday']
		month=e['FCTTIME']['mon']
		year=e['FCTTIME']['year']
		hour=e['FCTTIME']['hour']
		temp=e['temp']['english']
		sky=e['sky']
		condition=e['condition']
		wspd=e['wspd']['english']
		wdir=e['wdir']['degrees']
		wc=e['windchill']['english']
		qpf=e['qpf']['english']
		snow=e['snow']['english']
		pres=e['mslp']['english']
		hum=e['humidity']
		qpf=float(qpf)
		snow=float(snow)
		pres=float(pres)
		db_date=str(year)+'-'+str(month)+'-'+str(day)
		db_out=[str(db_date),str(location),str(hour),str(temp),str(sky),str(condition),str(wspd),str(wdir),str(wc),str(qpf),str(snow),str(pres),str(hum)]
		q='insert into forecast(rec_date,rec_time,for_date,location,hour,temp,sky,cond,wspd,wdir,wc,qpf,snow,pres,hum) values(curdate(),curtime(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
		try:
			curs.execute(q,db_out)
			db.commit()
			#log.debug("entry added for location: "+location)
		except:
			db.rollback()
			log.error("Error Adding DB entry")
			log.error(sys.exc_info())
		
def set_last(location,what):
	q="UPDATE last_checked set "+what+" = Now() where location=%s"
	try:
		curs.execute(q,[location,])
		db.commit()
	except:
		db.rollback()
		log.error("Error setting current time in last_checked")
		log.error(sys.exc_info())
def get_forecast(location):
	global key, kindex
	log.info("Getting forcast for: "+location)
	url='http://api.wunderground.com/api/'+key[kindex]+'/hourly10day/q/OR/'+location+'.json'
	try:
		response=urllib.urlopen(url)
		data=json.loads(response.read())
	except:
		log.error("Error Getting Forecast from web")
		log.error(sys.exc_info())
		return
	parse_forecast(data,location)
	set_last(location,"forecast")
def get_current(location):
	log.error("FIXME: write function for get_current")
	set_last(location,"current")
def get_alert(location):
	log.error("FIXME: write funtion for get_alert")
	set_last(location,"alert")
def need_update():
	#check to see if anything needs update
	#will return location,type if any are found
	#for this code, we will only be looking at ones that have a repeat flag
	curs.execute("SELECT * FROM last_checked where rep=1")
	data=curs.fetchall()
	if len(data)==0:
		log.info("No Entrys set to Repeat")
	for line in data:
		location=line[0]
		tmp=time.strptime(str(line[1]),'%Y-%m-%d %H:%M:%S')	
		forecast_time=datetime.datetime(*tmp[:6])
		tmp=time.strptime(str(line[2]),'%Y-%m-%d %H:%M:%S')
		current_time=datetime.datetime(*tmp[:6])
		tmp=time.strptime(str(line[3]),'%Y-%m-%d %H:%M:%S')
		alert_time=datetime.datetime(*tmp[:6])
		cur=datetime.datetime.now()

		forecast_delta=(cur-forecast_time)
		forecast_delta=forecast_delta.seconds/60
		current_delta=(cur-current_time).seconds/60
		alert_delta=(cur-alert_time).seconds/60
		if forecast_delta>UT_FORECAST:
			get_forecast(location)
		if current_delta>UT_CURRENT:
			get_current(location)
		if alert_delta>UT_ALERT:
			get_alert(location)
def check_config():
	
	global UT_CURRENT,UT_FORECAST,UT_ALERT
	curs.execute("SELECT * FROM config")
	data=curs.fetchall()
	for line in data:
		if line[0]=='current_update':
			try:
				UT_CURRENT=int(line[1])
			except:
				log.error("error getting int from current_update")
		
		if line[0]=='alert_update':
			try:
				UT_ALERT=int(line[1])
			except:
				log.error("error getting int from alert_update")

		if line[0]=='forecast_update':
			try:
				UT_FORECAST=int(line[1])
			except:
				log.error("error getting int from forecast_update")
def test():
	log.debug("Running Test function")
	f=open('hourlyforcast_example','r')
	data=f.read()
	parse_forecast(data,"TEST")




if len(sys.argv)>1:

	if 't' in sys.argv[1]:
		TEST=True
		test()
		exit()


locations=[]
locations.append('albany');
locations.append('portland');
locations.append('eugene');
locations.append('newport');
while True:
	#main loop
	log.info("Weather Process starting....")
	for l in locations:
		#get_forecast(l)
		#time.sleep(60*60*2)
		need_update()
		check_config()
		time.sleep(10)
