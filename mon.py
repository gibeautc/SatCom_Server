#!/usr/bin/env python

import MySQLdb
import time
print("Starting to mon for login failure")
db=MySQLdb.connect(host="localhost",user="root",passwd="aq12ws",db="main")
curs=db.cursor()

q="SELECT id from unauth order by id desc limit 1"
start=0
curs.execute(q)
i=curs.fetchone()
start=int(i[0])
start=start-10
if start<0:
	start=0
i=curs.fetchall()
print("Starting index: "+str(start))
#curs.close()
cnt=0
while True:


	q='SELECT * FROM unauth WHERE id > %s'
	curs.execute(q,start)
	data=curs.fetchall()
	for line in data:
		print(line[2]+" : "+line[3])
		start=line[4]
		cnt=cnt+1
		if cnt==10:
			print("*******END OLD******")
	#curs.close()
	db.commit()
	time.sleep(5)
	

