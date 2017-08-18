#!/usr/bin/env python
import MySQLdb
import sys
import datetime
import time


up=u"\u25B2"
down=u"\u25BC"
class bcolors:
	BLUE='\033[0;37;44m'
	ENDC='\033[0m'



db=MySQLdb.connect("localhost","auto","myvice12","main")
curs=db.cursor()

for x in range(3):
	z1s=0
	z2s=0
	z3s=0
	z4s=0
	count=0	
	curs.execute("select * from dt where dayofweek(tdate)=dayofweek(current_date()) and hour(ttime)=hour(date_add(now(),interval "+str(x)+" hour))")
	data=curs.fetchall()
	for entry in data:
		if entry[2]>-5:
			z1s+=entry[2]
			count+=1
	z1s_ave=float(z1s/count)
	
	count=0
	for entry in data:
		if entry[3]>-5:
			z2s+=entry[3]
			count+=1
	z2s_ave=float(z2s/count)
	
	count=0
	for entry in data:
		if entry[4]>-5:
			z3s+=entry[4]
			count+=1
	z3s_ave=float(z3s/count)
	
	count=0
	for entry in data:
		if entry[5]>-5:
			z4s+=entry[5]
			count+=1
	z4s_ave=float(z4s/count)
	count=0	



	total=z1s_ave+z2s_ave+z3s_ave+z4s_ave
	print(str(x)+": "+str(total))
print("Closing Database and exiting")
db.close()
