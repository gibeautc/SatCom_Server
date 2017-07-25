#!/usr/bin/env python
import MySQLdb
import subprocess
import time
import sys
db=MySQLdb.connect("localhost","root","myvice12","main")
curs=db.cursor()


def db_add(title,notes,typ,location,owner):
	text="insert into issues(ddate,ttime,title,notes,type,location,status,owner)" 
	text=text+' values(current_date(),now(),%s,%s,%s,%s,"N",%s)'
	data=(title,notes,typ,location,owner)
	#print text
	try:
		curs.execute(text,data)
		db.commit()
	except:
		print("DB Error, rolling back....")
		db.rollback()	

def open_issues(t):
	if(t=="all" or t==""):
		curs.execute("select id,title from issues where status!='D'")
		data=curs.fetchall()
		for e in data:
			print e
	else:
		curs.execute("select id,title from issues where status !='D' and type=%s",t)
		data=curs.fetchall()
		for e in data:
			print e
def show_all():
	curs.execute("select id,title,type,status from issues")
	data=curs.fetchall()
	for e in data:
		print e
def detail(i):
	curs.execute("select * from issues where id="+i)
	data=curs.fetchone()
	print("Title: " +data[3])
	print("Notes: " +data[4])
if(len(sys.argv)==1):
	print("No Argument given")
elif(sys.argv[1]=='add'):
	print("Adding new Issue")
	t=raw_input("Title of Issue:")
	n=raw_input("Notes:")
	ttype=raw_input("\n\nType?\nSP-Server side python\nCP-Client Side python\nSB-Server Side DB\nCB-Client side DB\nW-web_interface\nH-Hardware:")
	#need to check this input for correctness
	loc=raw_input("Location(file name or peice of hardware effected):")
	o=raw_input("Your Name:")
	
	#print all info
	print("Title: "+t)
	print("Notes: "+n)
	print("Type: "+ttype)
	print("Location: "+loc)
	print("Owner: "+o)

	acc=raw_input("Is this correct?")
	if(acc=="y" or acc=="yes"):
		db_add(t,n,ttype,loc,o)
elif(sys.argv[1]=='open'):
	a=raw_input("Of what type(SP,CP,SB,CP,H,W):")
	open_issues(a)
elif(sys.argv[1]=='show'):
	detail(sys.argv[2])
elif(sys.argv[1]=='all'):
	show_all()
