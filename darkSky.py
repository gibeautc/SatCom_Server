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
import filelock
TEST=False


pidFile="/home/pi/logs/"+os.path.basename(__file__)+".pid"
f=open(pidFile,"w")
f.close()

lock=filelock.FileLock(pidFile)
lock.timeout=1
lock.acquire()



#Todo
#add database backup functionality
#add state to location names so that we can do stuff outside of oregon
#convert weather to urllib2 since I think its better?
#remove text name from river data, look it up via river_sites and will save a ton of space in the long run


db=MySQLdb.connect('localhost','root','aq12ws','darksky')
curs=db.cursor()



#used for md5 checksum
start=True
md=0


log.basicConfig(filename='/home/pi/logs/darkSky.log',level=log.DEBUG,format='%(asctime)s %(levelname)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def webResponse(loc):
	urlApi='https://api.darksky.net/forecast/304e4f1db901c61cf8cb2b6d9be6237a/'
	st=time.time()
	try:
		response=urllib2.urlopen(urlApi+loc)
	except:
		log.error("Response Fail")
		log.error(urlApi+loc)
		log.error(sys.exc_info())
		return None
	try:
		html=response.read()
	except:
		log.error("Failed to read response")
		log.error(urlApi+loc)
		return None
	try:
		jsonData=json.loads(html)
	except:
		log.error("Failed to get JSON from response")
		log.error(urlApi+loc)
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
        pass
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

def parseCurrent(locId,data):
	log.debug(data)
	log.info("Adding current conditions for "+str(locId))
	fields=[]
	values=[]
	fields.append("recTime")
	fields.append("locId")
	values.append(str(locId))
	
	
	try:
		tmp=data['summary']
		values.append(str(tmp))
		fields.append("summary")
	except:
		pass
		
	try:
		tmp=data['precipIntensity']
		values.append(str(tmp))
		fields.append("precipInt")
	except:
		pass
		
	try:
		tmp=data['precipProbability']
		values.append(str(tmp))
		fields.append("precipProb")
	except:
		pass
	
	try:
		tmp=data['precipType']
		values.append(str(tmp))
		fields.append("precipType")
	except:
		pass
	
	try:
		tmp=data['temperature']
		values.append(str(tmp))
		fields.append("temp")
	except:
		pass
		
	try:
		tmp=data['pressure']
		values.append(str(tmp))
		fields.append("pressure")
	except:
		pass
		
	try:
		tmp=data['windSpeed']
		values.append(str(tmp))
		fields.append("windSpeed")
	except:
		pass
		
	try:
		tmp=data['windGust']
		values.append(str(tmp))
		fields.append("windGust")
	except:
		pass	
		
	try:
		tmp=data['windBearing']
		values.append(str(tmp))
		fields.append("windDir")
	except:
		pass
		
	try:
		tmp=data['nearestStormBearing']
		values.append(str(tmp))
		fields.append("stormDir")
	except:
		pass
		
	try:
		tmp=data['nearestStormDistance']
		values.append(str(tmp))
		fields.append("stormDist")
	except:
		pass	
		
	try:
		tmp=data['cloudCover']
		values.append(str(int(float(tmp)*100)))
		fields.append("sky")
	except:
		pass
		
	q='insert into current('
	for i in range(len(fields)):
		q=q+fields[i]
		if i<len(fields)-1:
			q=q+","
	q=q+")"
	q=q+" values(Now(),"
	for i in range(len(values)):
		q=q+"%s"
		if i<len(values)-1:
			q=q+","
	q=q+")"
	try:
		log.info("commiting current")
		curs.execute(q,values)
		db.commit()
	except:
		log.error("Error Adding DB entry(current)")
		db.rollback()
		log.error(sys.exc_info())
			
def parseDaily(locId,data):
	log.debug(data)
	log.info("Adding Daily Forecast for "+str(locId))
	days=data['data']
	for d in days:
		fields=[]
		values=[]
		fields.append("fdate")
		fields.append("locId")
		values.append(str(locId))
		
		try:
			tmp=d['time']
			tmp=int(tmp)
			#now need to make it a datetime string for mysql
			tmp=datetime.datetime.fromtimestamp(tmp).strftime('%Y-%m-%d %H:%M:%S')
			values.append(str(tmp))
			fields.append("ddate")
		except:
			pass
			
		try:
			tmp=d['sunriseTime']
			tmp=int(tmp)
			#now need to make it a datetime string for mysql
			tmp=datetime.datetime.fromtimestamp(tmp).strftime('%Y-%m-%d %H:%M:%S')
			values.append(str(tmp))
			fields.append("sunrise")
		except:
			pass
			
		try:
			tmp=d['sunsetTime']
			tmp=int(tmp)
			#now need to make it a datetime string for mysql
			tmp=datetime.datetime.fromtimestamp(tmp).strftime('%Y-%m-%d %H:%M:%S')
			values.append(str(tmp))
			fields.append("sunset")
		except:
			pass
		
		try:
			tmp=d['summary']
			values.append(str(tmp))
			fields.append("summary")
		except:
			pass
			
		try:
			tmp=d['precipIntensity']
			values.append(str(tmp))
			fields.append("precipInt")
		except:
			pass
		
		try:
			tmp=d['precipIntensityMax']
			values.append(str(tmp))
			fields.append("precipMaxInt")
		except:
			pass
			
		try:
			tmp=d['precipIntensityMaxTime']
			tmp=int(tmp)
			#now need to make it a datetime string for mysql
			tmp=datetime.datetime.fromtimestamp(tmp).strftime('%Y-%m-%d %H:%M:%S')
			values.append(str(tmp))
			fields.append("precipMaxTime")
		except:
			pass
			
		try:
			tmp=d['temperatureMaxTime']
			tmp=int(tmp)
			#now need to make it a datetime string for mysql
			tmp=datetime.datetime.fromtimestamp(tmp).strftime('%Y-%m-%d %H:%M:%S')
			values.append(str(tmp))
			fields.append("timeHight")
		except:
			pass
			
		try:
			tmp=d['temperatureMinTime']
			tmp=int(tmp)
			#now need to make it a datetime string for mysql
			tmp=datetime.datetime.fromtimestamp(tmp).strftime('%Y-%m-%d %H:%M:%S')
			values.append(str(tmp))
			fields.append("timeLow")
		except:
			pass
			
		try:
			tmp=d['precipProbability']
			values.append(str(tmp))
			fields.append("precipProb")
		except:
			pass
		
		try:
			tmp=d['precipType']
			values.append(str(tmp))
			fields.append("precipType")
		except:
			pass
		
		try:
			tmp=d['temperature']
			values.append(str(tmp))
			fields.append("temp")
		except:
			pass
		try:
			tmp=d['temperatureMax']
			values.append(str(tmp))
			fields.append("tempHigh")
		except:
			pass
		
		try:
			tmp=d['temperatureMin']
			values.append(str(tmp))
			fields.append("tempLow")
		except:
			pass
			
		try:
			tmp=d['pressure']
			values.append(str(tmp))
			fields.append("pressure")
		except:
			pass
			
		try:
			tmp=d['windSpeed']
			values.append(str(tmp))
			fields.append("windSpeed")
		except:
			pass
			
		try:
			tmp=d['windGust']
			values.append(str(tmp))
			fields.append("windGust")
		except:
			pass	
			
		try:
			tmp=d['windBearing']
			values.append(str(tmp))
			fields.append("windDir")
		except:
			pass
					
		try:
			tmp=d['cloudCover']
			values.append(str(int(float(tmp)*100)))
			fields.append("sky")
		except:
			pass
			
		q='insert into daily('
		for i in range(len(fields)):
			q=q+fields[i]
			if i<len(fields)-1:
				q=q+","
		q=q+")"
		q=q+" values(Now(),"
		for i in range(len(values)):
			q=q+"%s"
			if i<len(values)-1:
				q=q+","
		q=q+")"
		try:
			log.info(q)
			log.info(values)
			log.info("commiting Daily Record")
			curs.execute(q,values)
			db.commit()
		except:
			log.error("Error Adding DB entry(Conditions)")
			db.rollback()
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
	q="UPDATE locations set lastchecked= Now() where id=%s"
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
	#url="https://api.darksky.net/forecast/304e4f1db901c61cf8cb2b6d9be6237a/"
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
	#check to see if anything needs update
	#will return location,type if any are found
	#for this code, we will only be looking at ones that have a repeat flag
	cur=datetime.datetime.now()
	curs.execute("SELECT * FROM locations where rec>0")
	data=curs.fetchall()
	if len(data)==0:
		log.info("No Entrys set to Repeat")
	for line in data:
		location=line[0] #need new index
		tmp=time.strptime(str(line[4]),'%Y-%m-%d %H:%M:%S')
		forecast_time=datetime.datetime(*tmp[:6])

		forecast_delta=(cur-forecast_time)
		forecast_delta=forecast_delta.seconds/60 #should be in minutes now
		rep=line[5]
		locId=line[0]
		loc=str(line[2])+","+str(line[3])
		#if rep==1:
			#get_forecast()
			#set rep=0
			#set lastChecked
			#continue
		if rep==2 and forecast_delta>15:
			forecast=webResponse(loc)
			if forecast is not None:
				set_last(locId)
			else:
				continue
		else:
			continue
		#if rep==3 && delta>60*24:
			#get_forecast()
			#set lastChecked
			#continue
		try:
			c=forecast['currently']
			log.debug(c)
			parseCurrent(locId,c)
		except:
			log.debug("No Current Data for locId: "+str(locId))
			log.error(sys.exc_info())
			
		try:
			d=forecast['daily']
			log.debug(d)
			parseDaily(locId,d)
		except:
			log.debug("No Daily Data for locId: "+str(locId))
			log.error(sys.exc_info())
			
			
			
		#getForecast should now take (id,lat,lon,name)

def main():
	log.info("DarkSky Process starting....")
	startLogs=5
	while True:
		check_md5()
		need_update()
		#check_send_alert()
		time.sleep(10)
		if startLogs>0:
			startLogs=startLogs-1
			log.debug("Tick")


if __name__=="__main__":
	main()
