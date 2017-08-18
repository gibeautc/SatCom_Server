#!/usr/bin/env python
import subprocess
import time
import json
import urllib
import pprint
import MySQLdb
import sys
db=MySQLdb.connect('localhost','auto','myvice12','main')
curs=db.cursor()
key=["35859b32434c5985","803ee257021d3c0e"]
kindex=0
citys=['albany','salem','portland','newport','eugene']

rate=21

def change_key():
	global kindex
	kindex+=1
	if kindex>1:
		kindex=0
	return

def Get_current(city_name):
	global key,kindex
	print("Getting Current: "+city_name)
	url="http://api.wunderground.com/api/"+key[kindex]+"/conditions/q/OR/"+city_name+".json"
	try:
		response=urllib.urlopen(url)
		data=json.loads(response.read())
	except:
		print("Error Getting Data")
		print(sys.exc_info())
		return
	cur=data['current_observation']
	town=cur['display_location']['full']
	temp=cur['temp_f']
	wind=cur['wind_mph']
	weather=cur['weather']
	pressure=cur['pressure_in']
	pressure_trend=cur['pressure_trend']
	precip_today=cur['precip_today_in']
	db_out=[city_name,str(weather),str(temp),str(wind),str(pressure),str(pressure_trend),str(precip_today)]
	try:
		curs.execute('insert into weather_cur values(current_date(),now(),%s,%s,%s,%s,%s,%s,%s,0)',db_out)
		db.commit()
	except:
		print("Error: Rolling Back")
		db.rollback()
		print(sys.exc_info())


def Get_alert(city_name):
	global key,kindex
	print("Getting Alerts: "+city_name)
	url="http://api.wunderground.com/api/"+key[kindex]+"/alerts/q/OR/"+city_name+".json"
	try:
		response=urllib.urlopen(url)
		data=json.loads(response.read())
		alerts=data['alerts']
	except:
		change_key()
		print("Error Getting Data")
		print(sys.exc_info())
		return
	for alert in alerts:
		issued=alert['date']
		description=alert['description']
		expires=alert['expires']
		message=alert['message']
		#print("Alerts for: "+city_name)
		#print(issued)
		#print("Expires: "+expires)
		#print(description)
		#print(message)
		db_out=[str(issued),str(expires),str(description),str(message),str(1),city_name]
		try:
			check='select* from weather_alert where description="'+str(description)+'" and city="'+city_name+'" and active=1'
			curs.execute(check)
			dup=curs.fetchall()
			for r in dup:
				d='delete from weather_alert where id='+str(r[8])
				curs.execute(d)
				print("Dup Removed")
			print(len(dup))
		except:
			print("Error Checking Dups")
			print(sys.exc_info())
		try:
			curs.execute('insert into weather_alert values(current_date(),now(),%s,%s,%s,%s,%s,%s,0)',db_out)
			db.commit()
		except:
			print("Error: Rolling Back")
			db.rollback()
			print(sys.exc_info())




def Get_forecast(city_name):
	global key, kindex
	url="http://api.wunderground.com/api/"+key[kindex]+"/forecast10day/q/OR/"+city_name+".json"
	print("Getting Forecast: "+city_name)
	try:
		response=urllib.urlopen(url)
		data=json.loads(response.read())
	except:
		print("Error Getting Data")
		print(sys.exc_info())
		return
	try:
		forcast=data['forecast']['simpleforecast']['forecastday']
	except:
		change_key()
		print("Forcast Error:")
		print(data)
		return
	for day in forcast:
		status=day['conditions']
		high=day['high']['fahrenheit']
		low=day['low']['fahrenheit']
		wind_mph=day['avewind']['mph']
		wind_dir=day['avewind']['dir']
		wind_max=day['maxwind']['mph']
		wind_mdir=day['maxwind']['dir']
		date_day=day['date']['day']
		date_month=day['date']['month']
		date_year=day['date']['year']
		snow_day=day['snow_day']['in']
		snow_night=day['snow_night']['in']
		snow_total=day['snow_allday']['in']
		qpf_day=day['qpf_day']['in']
		qpf_night=day['qpf_night']['in']
		qpf_total=day['qpf_allday']['in']
		#sql date format YYYY-MM-DD
		#Will need to check if single digit day and month are right
		db_date=str(date_year)+"-"+str(date_month)+"-"+str(date_day)
		db_out=[db_date,str(high),str(low),str(wind_mph),wind_dir,str(wind_max),wind_mdir,str(qpf_day),str(qpf_night),str(qpf_total),str(snow_day),str(snow_night),str(snow_total),status,city_name]
		try:
			curs.execute('insert into weather_forecast values(current_date(),now(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0)',db_out)
			db.commit()
		except:
			print("Error: Rolling Back")
			db.rollback()
			print(sys.exc_info())



while True:
	time.sleep(120)
	if rate>20:
		print("Starting Loop\n\n")
		rate=0
		for city in citys:
			Get_forecast(city)
			Get_alert(city)
			time.sleep(120)
	for city in citys:
		Get_current(city)
		time.sleep(120)
	time.sleep(120)
	rate+=1
		
	
