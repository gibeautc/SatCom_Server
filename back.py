#!/usr/bin/env python

import MySQLdb
import time
import subprocess
def check_in_db(ip):
	#check how many times ip address is in database
	q="SELECT * from unauth where ip_address=%s"
	curs.execute(q,ip)
	i=curs.fetchall()
	return len(i)
print("BackFilling ip address table")
db=MySQLdb.connect(host="localhost",user="root",passwd="aq12ws",db="main")
curs=db.cursor()
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


def update(stat):
	if stat==0:
		q="SELECT ip from ip_list"
	if stat==1:
		q="SELECT ip from ip_list where country is null"
	curs.execute(q)
	i=curs.fetchall()
	for line in i:
		ip=line[0]
		time.sleep(.5)
		print("Updating:"+ip+'|')
		#try:
		data=subprocess.check_output(['whois',ip])
		data=data.split("\n")
		for l in data:
			if "Country" in l or "country" in l:
				l=l.split(" ")
				
				print(l[8])
				cntry=country(l[8])
				q="update ip_list set country=%s where ip=%s"
				#try:
				curs.execute(q,(cntry,ip))
				db.commit()
				#except:
				#	db.rollback()
				#	print("DB error")
		#except:
		#	print("Error in updating: "+ip)
	
def check_in_list(ip):
	q="SELECT * from ip_list where ip=%s"
	curs.execute(q,ip)
	i=curs.fetchall()
	
	return len(i)

def add_to_list(ip,h):
	print("Adding "+ip+" to list")
	q="insert into ip_list(ip,block) values(%s,%s)"
	if h>9:
		b=1
	else:
		b=0
	curs.execute(q,(ip,b))
	db.commit()



q="SELECT * from unauth"
curs.execute(q)
i=curs.fetchall()
for line in i:
	#check if ip is in ip table
	#keep local list to limit db calls?
	#if it is, just contine
	#if not, when we check for it, we will get a count
	#run a whois on it
	#store country and IP in database
	#other info that we want to keep can be put into a json object
	#and stored in the info text field
	c=check_in_list(line[2])	
	if c==0:
		cnt=check_in_db(line[2])
		add_to_list(line[2],cnt)
		#not in there
	elif c==1:
		#is in there alread
		print("Alread in List")
	else:
		print("ERROR, shouldnt be in there more then once")
		#error, shouldnt be in there twice
update(1)
	

