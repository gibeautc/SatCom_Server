#!/usr/bin/env python
import time
import sys
import json
import logging
import MySQLdb
import urllib

db=MySQLdb.connect('localhost','root','aq12ws','weather')
curs=db.cursor()
key=["35859b32434c5985","803ee257021d3c0e"]
kindex=0



TEST=False

import logging as log
log.basicConfig(filename='/home/pi/log/weather.log',level=logging.DEBUG,format='%(asctime)s %(levelname)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


def parse_forecast(data,location):
	#data=json.loads(data)
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
		if TEST:
			log.debug("Test")
		else:
			log.info("Adding record for location: "+location)
			db_date=str(year)+'-'+str(month)+'-'+str(day)
			db_out=[str(db_date),str(location),str(hour),str(temp),str(sky),str(condition),str(wspd),str(wdir),str(wc),str(qpf),str(snow),str(pres),str(hum)]
			q='insert into forecast(rec_date,rec_time,for_date,location,hour,temp,sky,cond,wspd,wdir,wc,qpf,snow,pres,hum) values(curdate(),curtime(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
			try:
				curs.execute(q,db_out)
				db.commit()
				log.debug("entry added for location: "+location)
			except:
				db.rollback()
				log.error("Error Adding DB entry")
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
	for l in locations:
		get_forecast(l)
		time.sleep(60*60*2)
