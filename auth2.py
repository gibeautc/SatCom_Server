#!/usr/bin/env python

import os
import errno
import MySQLdb

db=MySQLdb.connect(host="localhost",user="root",passwd="aq12ws",db="main")
curs=db.cursor()

#need database calls to pull existing blocked list
blocked=[]
ip_list={}

FIFO='authpipe'

def logout(msg):
	l=open('blocklog','a+')
	l.write(str(msg))
	l.write('\n')
	l.close()

try:
	os.mkfifo(FIFO)
except OSError as oe:
	if oe.errno != errno.EEXIST:
		raise

def check(ip,name):
	print("Checking IP: "+ip+" with username: "+name)
	if ip not in ip_list:
		ip_list[ip]=1
	else:
		ip_list[ip]=ip_list[ip]+1
	if ip not in blocked:
		if ip_list[ip]>10:
			#block them
			logout("Blocking: "+str(ip))
			os.system("sudo iptables -A INPUT -s "+ip+" -j DROP")
			blocked.append(ip)
	curs.execute("""INSERT INTO unauth(ddate,ttime,ip_address,username) VALUES(CURDATE(),CURTIME(),%s,%s)""",(ip,name))
	db.commit()

with open(FIFO,"r") as pipe:
	while True:
		data=pipe.readline()
		if data !="":

			if "Failed password for invalid" in data:
				elements=data.split(" ")
				ip=elements[12]
				name=elements[10]
				check(ip,name)
					
			elif "Failed password" in data:
				elements=data.split(" ")
				#get ip and name
				ip=elements[10]
				name=elements[8]
				check(ip,name)
		
	time.sleep(1)
db.close()
