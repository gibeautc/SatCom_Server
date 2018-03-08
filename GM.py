#!/usr/bin/env python


import logging
import MySQLdb


#could add make a gm class to contain these variables
#group ID
group_id=['1523559','27306241','29079593']
#        [    Crew ,bot test ,   boat   ,]

sec_id='0111eaa305c26110dd21040a0a'
sec_test_id='6156eb1065fb54295ea8ae138d'
ariana_id='481baace72a55ebbb9488e296e'


db=MySQLdb.connect('localhost','root','aq12ws','gm')
curs=db.cursor()


def db_connect():
	global db,curs
	db=MySQLdb.connect('localhost','root','aq12ws','gm')
	curs=db.cursor()


def add_signup(person,event,item):
	db_connect()
	logging.info("Adding to Signup for person: "+person+":"+event+":"+item)
	db_out=[str(person),str(event),str(item)]
	q='insert into signup(person,event,item) values(%s,%s,%s)'
	try:
		curs.execute(q,db_out)
		db.commit()
		#log.debug("entry added for location: "+location)
	except:
		db.rollback()
		logging.error("Error Adding DB entry")
		logging.error(sys.exc_info())
		
		
def add_event(name,date):
	db_connect()
	logging.info("Adding to Event List: "+name+":"+date)
	db_out=[str(name),str(date)]
	q='insert into events(name,ddate) values(%s,%s)'
	try:
		curs.execute(q,db_out)
		db.commit()
	except:
		db.rollback()
		logging.error("Error Adding DB entry")
		logging.error(sys.exc_info())
		
				
def get_event_list():
	q="select name from events"
	curs.execute(q)
	data=curs.fetchall()
	return data
def get_event(event):
	q="select name,ddate,ttime,location from events where id=%s"
	curs.execute(q,(event,))
	data=curs.fetchall()
	return data
def get_signup_for_event(event):
	db.commit()
	q="select person,item from signup where event=%s"
	curs.execute(q,(event,))
	data=curs.fetchall()
	return data
	 

def send_gm(message,bot):
	params=urllib.urlencode({'bot_id':bot,'text':message})
	f=urllib.urlopen("https://api.groupme.com/v3/bots/post",params)
	logging.debug(f.read())


def Sec_Start(ID,name,message,group):
	logging.debug("In Secretary Mode")
	if group==group_id[0]:
		bot_id=sec_id
	else:
		bot_id=sec_test_id
	if message[0]=='%':
		logging.debug("Got the %")
		if len(message)==1:
			#send the help info
			out="Hello "+name+"\nSend %E to see list of events"
			#out="hello"
			send_gm(out,bot_id)
			return
		if message[1]=="E":
			if len(message)==2:
				events=get_event_list()
				msg=""
				cnt=1
				if events is None:
						send_gm("No Events at this time",bot_id)
						return
				for e in events:
					msg=msg+"("+str(cnt)+")"+str(e[0])+"\n"
					cnt=cnt+1
				logging.debug(msg)
				send_gm(msg,bot_id)
				
				#get list of events
				#give them to user 
				#(1) Name Date
				#(2) Name
				#then say
			elif len(message)==3:
				try:
					event=message[2]
					data=get_event(event)
					#name,ddate,ttime,location
					e=data[0]
					msg=e[0]+" Will be on "+str(e[1])+"\n"
					signlist=get_signup_for_event(event)
					for s in signlist:
						msg=msg+str(s[0])+":"+str(s[1])+"\n"
					#will also need to get signup info and add that
					send_gm(msg,bot_id)
				except:
					logging.warning("Cant get Event info from message")
					send_gm("Cant Get Event Info From Database",bot_id) 
			else:
				#adding to sign up
				try:
					event=message[2]
					what=message[4:]
					logging.info(str(ID)+":"+str(event)+":"+str(what))
					add_signup(name,event,what)
					send_gm("Thanks! you are signed up for:" +what,bot_id)
				except:
					logging.error("Error adding to sign up")
					send_gm("Error Adding to sign up",bot_id)
					logging.error(sys.exc_info())
		if message[1]=='A':
			#adding an event
			if len(message)==2:
				send_gm("To Add event type %A EventName,2017-1-1",bot_id)
				return
			else:
				data=message.split(",")
				name=data[0].split(" ")
				name=name[1]
				date=data[1]
				try:
					add_event(name,date)
					send_gm("Event added:"+name,bot_id)
				except:
					send_gm("Error Adding Event",bot_id)	
