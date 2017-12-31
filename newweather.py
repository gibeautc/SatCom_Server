#!/usr/bin/env python
import time
import sys
import json
import MySQLdb
import urllib
import datetime
import os
import subprocess
import MySQLdb 
import logging as log
import urllib2

TEST=False

#Todo
#add database backup functionality
#add state to location names so that we can do stuff outside of oregon
#convert weather to urllib2 since I think its better?
#remove text name from river data, look it up via river_sites and will save a ton of space in the long run



#add key rotate functionality

alert_types=['HUR','TOR','TOW','WRN','SEW','WIN',
			'FLO','WAT','WND','SVR','HEA','HEA','FOG',
			'FOG','SPE','FIR','VOL','HWW','REC','REP','PUB']

alert_strings=['Hurricane Local Statement','Tornado Warning',
				'Tornado Watch','Severe Thunderstorm Warning',
				'Severe Thunderstorm Watch','Winter Weather Advisory',
				'Flood Warning','Flood Watch / Statement',
				'High Wind Advisory','Severe Weather Statement',
				'Heat Advisory','Dense Fog Advisory',
				'Special Weather Statement','Fire Weather Advisory',
				'Volcanic Activity Statement','Hurricane Wind Warning',
				'Record Set','Public Reports',
				'Public Information Statement']







db=MySQLdb.connect('localhost','root','aq12ws','weather')
curs=db.cursor()

#keys and index for weather api
weather_key=["35859b32434c5985","803ee257021d3c0e"]
kindex=0

#update times (min)
UT_FORECAST=2
UT_CURRENT=0.5
UT_ALERT=3
#types
FORECAST=0x01
CURRENT=0x02
ALERT=0x03

#used for md5 checksum
start=True
md=0


log.basicConfig(filename='/home/pi/logs/weather.log',level=log.DEBUG,format='%(asctime)s %(levelname)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def send_gm(message):
	bot='0111eaa305c26110dd21040a0a'	#real
	#bot='6156eb1065fb54295ea8ae138d'  #test
	params=urllib.urlencode({'bot_id':bot,'text':message})
	f=urllib.urlopen("https://api.groupme.com/v3/bots/post",params)
	log.debug(f.read())


def check_send_alert():
	db_out="select description,issued,expires from alert where location='albany' and notify<1"
	curs.execute(db_out,)
	data=curs.fetchall()
	new=0
	for d in data:
		new=1
		msg="Alert: "+str(d[0])+" ISSUED:"+str(d[1])+" EXPIRES:"+str(d[2])
		send_gm(msg)
		db_out="update alert set notify=1 where issued='"+str(d[1])+"' and location='albany' and expires='"+str(d[2])+"'"
		try:
			curs.execute(db_out,)
			db.commit()
			
		except:
			db.rollback()
			log.error("Error Updating Alert entry")
			log.error(sys.exc_info())
	if new==1:
		send_gm("Get more information at")
		send_gm("http://dustoff.servebeer.com")

def is_LatLon(location):
	print("checking if LatLon")
	#return true if location is lat/long
	#return false if not (this is because it is a city name)




def check_md5():
	global start,md
	tmd=subprocess.check_output(['md5sum',__file__])
	tmd=tmd.split(" ")
	tmd=tmd[0]
	if start:
		md=tmd
		start=False
		return
	if tmd!=md:
		log.error("Source Code Changed.... restarting")
		os.execl(sys.executable,sys.executable,*sys.argv)

	

def parse_river_file(j):
	height=0.0
	flow=0.0
	#print("Parsing file")
	try:
		value=j['value']
		ts=value['timeSeries']
		for val in ts:
			name=val['variable']['variableName']
			if 'flow' in name:
				flow=float(val['values'][0]['value'][0]['value'])
				#print(flow)
			if 'height' in name:
				height=float(val['values'][0]['value'][0]['value'])
				#print(flow)
	except:
		log.error("Error Parsing Data")
		return None
	#at this point we only want gauge height and flow rate
	return [height,flow]   #ft,cfs
	




	return [height,flow]

def get_river_data(ID):
	log.info("Getting Current Stats for station: "+str(ID))
	try:
		response = urllib2.urlopen('https://waterservices.usgs.gov/nwis/iv/?format=json&sites='+str(ID)+'&parameterCd=00060,00065&siteStatus=all')
		html = response.read()
		out=json.loads(html)
		return out
	except:
		log.error("Failed to get River data:"+str(ID))
		log.error(sys.exc_info())
		return None

def store_river(ID,location,height,flow):
	#takes in int ID, location [height,flow]
	db_out=[str(ID),str(location),str(height),str(flow)]
	q='insert into river_data(site_id,location,height,flow,rec_datetime) values(%s,%s,%s,%s,Now())'
	try:
		curs.execute(q,db_out)
		db.commit()
		#log.debug("entry added for location: "+location)
	except:
		db.rollback()
		log.error("Error Adding DB entry")
		log.error(sys.exc_info())


	
	

def parse_current(data,location):
	#data=json.loads(data)
	log.info("Adding current conditions for "+location)
	cur=data['current_observation']
	weather=cur['weather']
	temp=cur['temp_f']
	wind_dir=cur['wind_degrees']
	wind_dir=int(float(wind_dir))
	wind=cur['wind_mph']
	wind_gust=cur['wind_gust_mph']
	pressure=cur['pressure_in']
	pressure_trend=cur['pressure_trend']
	precip_1hr=cur['precip_1hr_in']
	precip_today=cur['precip_today_in']
	
	db_out=[str(location),str(weather),str(temp),str(wind_dir),str(wind),str(wind_gust),str(pressure),str(pressure_trend),str(precip_1hr),str(precip_today)]
	q='insert into conditions(rec_time,location,weather,temp,wind_dir,wind,wind_gust,pressure,pressure_trend,precip_1hr,precip_today) values(Now(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
	try:
		curs.execute(q,db_out)
		db.commit()
		#log.debug("entry added for location: "+location)
	except:
		db.rollback()
		log.error("Error Adding DB entry(Conditions)")
		log.error(sys.exc_info())
			
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
			log.error("Error Adding DB entry(Forecast)")
			log.error(sys.exc_info())
	
def parse_alert(data,location):
	
	log.info("Parsing Alert for "+location)
	alerts=data['alerts']
	for a in alerts:
		try:
			tp=a['type']
			issue=int(a['date_epoch'])
			expire=int(a['expires_epoch'])
			message=a['message']
			desc=a['description']
			iT=time.localtime(issue)
			eT=time.localtime(expire)
			issueStr=str(iT.tm_year)+"-"+str(iT.tm_mon)+"-"+str(iT.tm_mday)+" "+str(iT.tm_hour)+":"+str(iT.tm_min)+":"+str(iT.tm_sec)
			expireStr=str(eT.tm_year)+"-"+str(eT.tm_mon)+"-"+str(eT.tm_mday)+" "+str(eT.tm_hour)+":"+str(eT.tm_min)+":"+str(eT.tm_sec)
			db_out=[location,str(tp),str(desc),str(message),issueStr,expireStr]
			q='insert into alert(location,type,description,message,issued,expires,notify,active) values(%s,%s,%s,%s,%s,%s,0,1) on duplicate key update active=1'
		
			curs.execute(q,db_out)
			db.commit()
			log.debug("Alert entry added for location: "+location)
		except:
			db.rollback()
			log.error("Error Adding DB entry(Forecast)")
			log.error(sys.exc_info())	
	
	
	
		
def set_last(location,what):
	q="UPDATE last_checked_weather set "+what+" = Now() where location=%s"
	try:
		curs.execute(q,[location,])
		db.commit()
	except:
		db.rollback()
		log.error("Error setting current time in last_checked")
		log.error(sys.exc_info())
		
def set_river_last(ID):
	ID=str(ID)
	q="UPDATE river_sites set last_checked= Now() where id=%s"
	try:
		curs.execute(q,[ID,])
		db.commit()
	except:
		db.rollback()
		log.error("Error setting current time in last_checked")
		log.error(sys.exc_info())



def get_forecast(location):
	global weather_key, kindex
	log.info("Getting forcast for: "+location)
	url='http://api.wunderground.com/api/'+weather_key[kindex]+'/hourly10day/q/OR/'+location+'.json'
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
	global weather_key, kindex
	log.info("Getting current conditions for: "+location)
	url='http://api.wunderground.com/api/'+weather_key[kindex]+'/conditions/q/OR/'+location+'.json'
	try:
		response=urllib.urlopen(url)
		data=json.loads(response.read())
	except:
		log.error("Error Getting Conditions from web")
		log.error(sys.exc_info())
		return
	parse_current(data,location)
	set_last(location,"current")



def get_alert(location):
	#set all alerts for this location to inactive, then if they are still in data they will be updated
	db_out="update alert set active=0 where location='"+location+"'"
	try:
		curs.execute(db_out,)
		db.commit()
			
	except:
		db.rollback()
		log.error("Error Setting all Alerts to inactive")
		log.error(sys.exc_info())
	
	
	
	global weather_key, kindex
	log.info("Getting Alert conditions for: "+location)
	url='http://api.wunderground.com/api/'+weather_key[kindex]+'/alerts/q/OR/'+location+'.json'
	try:
		response=urllib.urlopen(url)
		data=json.loads(response.read())
	except:
		log.error("Error Getting Alerts from web")
		log.error(sys.exc_info())
		return
	parse_alert(data,location)
	set_last(location,"alert")



def need_update():
	#check to see if anything needs update
	#will return location,type if any are found
	#for this code, we will only be looking at ones that have a repeat flag
	curs.execute("SELECT * FROM last_checked_weather where rep>0")
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
		if forecast_delta>int(line[4])*60*UT_FORECAST:
			get_forecast(location)
		if current_delta>int(line[4])*60*UT_CURRENT:
			get_current(location)
		if alert_delta>int(line[4])*60*UT_ALERT:
			get_alert(location)
		
def check_river_update():
	curs.execute("SELECT * FROM river_sites")
	data=curs.fetchall()
	if len(data)==0:
		log.error("No sites returned from river_sites")
		return
	for line in data:	
		site=line[0]  #ID field  site number
		location=line[1]
		tmp=time.strptime(str(line[2]),'%Y-%m-%d %H:%M:%S')	
		last_time=datetime.datetime(*tmp[:6])
		cur=datetime.datetime.now()
		delta=(cur-last_time).seconds
		#log.debug(str(delta))
		if (cur-last_time).seconds/60>60:
			log.info("Updating River Location: "+str(location))
			raw=get_river_data(site)
			if raw==None:
				return
			data=parse_river_file(raw)
			if data is not None:
				store_river(site,location,data[0],data[1])
				set_river_last(site)
			
def check_config():
	
	global UT_CURRENT,UT_FORECAST,UT_ALERT
	curs.execute("SELECT * FROM config")
	data=curs.fetchall()
	for line in data:
		if line[0]=='current_update':
			try:
				UT_CURRENT=float(line[1])
			except:
				log.error("error getting int from current_update")
		
		if line[0]=='alert_update':
			try:
				UT_ALERT=float(line[1])
			except:
				log.error("error getting int from alert_update")

		if line[0]=='forecast_update':
			try:
				UT_FORECAST=float(line[1])
			except:
				log.error("error getting int from forecast_update")



def test():
	log.debug("Running Test function")
	f=open('hourlyforcast_example','r')
	data=f.read()
	parse_forecast(data,"TEST")




def main():
	if len(sys.argv)>1:

		if 't' in sys.argv[1]:
			TEST=True
			test()
			exit()


	log.info("Weather Process starting....")
	startLogs=5
	while True:
		check_md5()
		need_update()
		check_config()
		check_river_update()
		check_send_alert()
		time.sleep(10)
		if startLogs>0:
			startLogs=startLogs-1
			log.debug("Tick")



if __name__=="__main__":
	main()
