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

sant=[]
def Get_current():
	url="https://waterservices.usgs.gov/nwis/iv/?format=json&indent=on&stateCd=or&period=P1D&parameterCd=00060,00065&siteStatus=all"
	try:
		response=urllib.urlopen(url)
		data=json.loads(response.read())
	except:
		print("Error Getting Data")
		print(sys.exc_info())
		return
	val=data['value']
	for key,value in data.iteritems():
		print(key)
	print("\n")
	for key, value in val.iteritems():
		print(key)
	ts=val['timeSeries']
	print("\n")
	for key,value in ts[0].iteritems():
		print(key)
	for t in ts:
		n=t['sourceInfo']['siteName']
		if 'SANTIAM' in n:
			if 'JEFFERSON' in n:
				print(n)
				sant.append(t)
	for place in sant:
		for key,value in place.iteritems():
			print(key)
		print(place['name'])
		values=place['values']
		for key in values:
			for k,v in key.iteritems():
				print(k)
		value=values['value']
		print('\n')
		for v in value:
			print(v)	
	#cur=data['current_observation']
	#town=cur['display_location']['full']
	#db_out=[city_name,str(weather),str(temp),str(wind),str(pressure),str(pressure_trend),str(precip_today)]
	#try:
	#	curs.execute('insert into weather_cur values(current_date(),now(),%s,%s,%s,%s,%s,%s,%s,0)',db_out)
	#	db.commit()
	#except:
	#	print("Error: Rolling Back")
	#	db.rollback()
	#	print(sys.exc_info())


Get_current()
		
	
