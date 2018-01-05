#!/usr/bin/env python
import time
import sys
import json
import MySQLdb
import datetime
import os
import subprocess
import logging as log
import urllib2

TEST=False

#Todo
#add database backup functionality
#add state to location names so that we can do stuff outside of oregon
#convert weather to urllib2 since I think its better?
#remove text name from river data, look it up via river_sites and will save a ton of space in the long run


db=MySQLdb.connect('localhost','root','aq12ws','darkSky')
curs=db.cursor()



#used for md5 checksum
start=True
md=0


log.basicConfig(filename='/home/pi/logs/darkSky.log',level=log.DEBUG,format='%(asctime)s %(levelname)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def webResponse(loc):
	st=time.time()
	try:
		response=urllib2.urlopen(urlApi+loc)
	except:
		log.error("Response Fail")
		log.error(url)
                log.error(sys.exc_info())
		return None
	try:
		html=response.read()
	except:
		log.error("Failed to read response")
		log.error(url)
		return None
	try:
		jsonData=json.loads(html)
	except:
		log.error("Failed to get JSON from response")
		log.error(url)
		return None
	et=time.time()
	log.debug("DarkSky Response time: "+str(et-st))
	return jsonData

def send_gm(message):
	bot='0111eaa305c26110dd21040a0a'	#real
	#bot='6156eb1065fb54295ea8ae138d'  #test
	params=urllib.urlencode({'bot_id':bot,'text':message})
	f=urllib.urlopen("https://api.groupme.com/v3/bots/post",params)
	log.debug(f.read())


def check_send_alert():
	#TODO  This will need a rewrite
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

def parse_current(data,location):
#TODO ReWrite ME!
	try:
		log.debug(data)
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
	except:
		log.error("Error Parsing Current Conditions for: "+location)
		log.error("Here is the data")
		log.error(data)
		log.error("Here is the error")
		log.error(sys.exc_info())
		return	
	db_out=[str(location),str(weather),str(temp),str(wind_dir),str(wind),str(wind_gust),str(pressure),str(pressure_trend),str(precip_1hr),str(precip_today)]
	q='insert into conditions(rec_time,location,weather,temp,wind_dir,wind,wind_gust,pressure,pressure_trend,precip_1hr,precip_today) values(Now(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
	try:
		log.info("commiting current")
		curs.execute(q,db_out)
		db.commit()
	except:
		log.error("Error Adding DB entry(Conditions)")
		db.rollback()
		log.error(sys.exc_info())
			
def parse_daily(data,location):
	#TODO ReWrite ME!!!
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
	#TODO ReWrite ME!!!
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
		
def set_last(locID):
	#Not Tested
	q="UPDATE locations set lastChecked= Now() where id=%s"
	try:
		curs.execute(q,[locID,])
		db.commit()
	except:
		db.rollback()
		log.error("Error setting current time for lastChecked")
		log.error(sys.exc_info())

def getForecast(ID,lat,lon,name):
	#will pull entire forecast for location, current,minutly,hourly,daily,alert
	#if they are available, decide if they are, and send to seperate parsing functions
	log.info("Getting forcast for: "+name)
	url="https://api.darksky.net/forecast/304e4f1db901c61cf8cb2b6d9be6237a/"
	#plus the lat,lon like 37.8267,-122.4233
	
	try:
		data=webResponse(url+str(lat)+","+str(lon))
		if data is None:
			return
	except:
		#should never get here, errors should be caught in webResponse
		log.error("Error Getting Forecast from web")
		log.error(response.read())
		log.error(sys.exc_info())
		return
	#check for each part, and send to parser
	#FINISH ME!!!!


def need_update():
	#TODO ReWrite ME!!!
	
	#check to see if anything needs update
	#will return location,type if any are found
	#for this code, we will only be looking at ones that have a repeat flag
	curs.execute("SELECT * FROM locations where rep>0")
	data=curs.fetchall()
	if len(data)==0:
		log.info("No Entrys set to Repeat")
	for line in data:
		location=line[0] #need new index
		tmp=time.strptime(str(line[1]),'%Y-%m-%d %H:%M:%S')	#need new index
		forecast_time=datetime.datetime(*tmp[:6])

		forecast_delta=(cur-forecast_time)
		forecast_delta=forecast_delta.seconds/60 #should be in minutes now
		#check If rep==1:
			#get_forecast()
			#set rep=0
			#set lastChecked
			#continue
		#if rep==2 && delta>15:
			#get_forecast()
			#set lastChecked
			#continue
		#if rep==3 && delta>60*24:
			#get_forecast()
			#set lastChecked
			#continue
			
		#getForecast should now take (id,lat,lon,name)

def main():
	log.info("DarkSky Process starting....")
	startLogs=5
	while True:
		check_md5()
		need_update()
		check_send_alert()
		time.sleep(10)
		if startLogs>0:
			startLogs=startLogs-1
			log.debug("Tick")


if __name__=="__main__":
	main()
