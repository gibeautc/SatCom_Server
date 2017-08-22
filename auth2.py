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

def check_in_db(ip):
	#check how many times ip address is in database
	q="SELECT * from unauth where ip_address=%s"
	curs.execute(q,ip)
	i=curs.fetchall()
	return len(i)

def country(tag):
	c={}
	c['US']='United States'
	c['CN']='China'
	c['EG']='Egypt'
	c['DE']='Germany'
	c['IL']='Israel'
	c['RU']='Russia'
	c['UY']='Uruguay'
	c['CA']='Canada'
	c['RO']='Romania'
	c['LU']='Luxembourg'
	c['TW']='Taiwan'
	c['NL']='Netherlands'
	c['CZ']='Czech Republic'
	c['IN']='India'
	c['UA']='Ukraine'
	c['SN']='Senegal'
	c['VN']='Viet Nam'
	c['LV']='Latvia'
	c['KR']='Korea, Republic'
	c['FR']='France'
	c['IR']='Iran'
	c['GB']='United Kingdom'
	if tag in c:
		return c[tag]
	else:
	return tag

def check_in_list(ip):
	q="SELECT * from ip_list where ip=%s"
	curs.execute(q,ip)
	i=curs.fetchall()
	
	return len(i)

def add_to_list(ip,h):
	print("Adding "+ip+" to list")
	data=subprocess.check_output(['whois',ip])
	data=data.split("\n")
	cntry=""
	for l in data:
		if "Country" in l or "country" in l:
			l=l.split(" ")
			print(l[8])
			cntry=country(l[8])

	q="insert into ip_list(ip,block,country) values(%s,%s,%s)"
	if h>9:
		b=1
	else:
		b=0
	curs.execute(q,(ip,b,cntry))
	db.commit()

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
	if check_in_list(ip)==0:
		add_to_list(ip,ip_list[ip])

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
