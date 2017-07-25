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

sunstart=9
sunend=15
print("Assuming good daylight hours from "+str(sunstart)+" to "+str(sunend)+" hours")
def check_sky(mon,day):
		curs.execute('select * from SatWeather where mon="'+str(mon)+'" and day="'+str(day)+'"')
		a=curs.fetchall()
		average=0
		cnt=0
		for l in a:
			if int(l[17])>=sunstart and int(l[17])<=sunend:
				average=average+int(l[13])
				cnt=cnt+1
		print("Sky Coverage for "+str(mon)+"/"+str(day)+" is: "+str(float(average/cnt))+" percent covered")
check_sky(2,21)	
check_sky(2,22)
check_sky(2,23)
check_sky(2,24)
