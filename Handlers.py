#!/usr/bin/env python

import logging
import MySQLdb
import time

wxdb=MySQLdb.connect('localhost','root','aq12ws','weather')
wxCurs=wxdb.cursor()

def findLocation():
	#need a valid loction ID from database, we have lat and long
	#in request data. Pull all locations, check if there is one that has
	#an acceptable distance   say 5 Miles?
	#if we have one return the ID, if not we need to add it in (with rec of 1)
	# and return new ID

def gm_message_rx(request):
	try:
		data=request.json
		logging.debug(data)
		name=data['name']
		ID=data['user_id']
		message=data['text']
		message=str(message)
		groupID=data['group_id']
		name=str(name)
		sender=data['sender_type']
		if sender!='bot':
			logging.debug("Message is: "+message)
			logging.debug("Message from: "+name)
			logging.debug("In Group: "+groupID)
		else:
			return
		if group_id.index(groupID)<2:
			Sec_Start(ID,name,message,groupID)
			return "done",200
		if message[0]=="$":
			logging.debug("got a $")
			if "Chad" in name:
				logging.debug("and its from me")
				#send message to sat
				IMEI='300234064380130'
				NAME="gibeautc@oregonstate.edu"
				PASSWORD='aq12ws'
				DATA=message[1:]
				params=urllib.urlencode({'imei':IMEI,'username':NAME,'password':PASSWORD,'data':DATA.encode("hex")})
				f=urllib.urlopen("https://core.rock7.com/rockblock/MT",params)
				print(f.read())
				logging.debug(str(f.read()))
				#send_gm('Thanks Chad, your message of: "'+DATA+'" has been sent to the que')
			else:
				#not authorized
				try:
					name=name.split(" ")
					name=name[0]
				except:
					name=name
				#send_gm("Sorry "+name+" , you are not authorized to send messages at this time.....please fuck off")
		#print("GM Message from: "+str(name)+" ----:"+str(message))
	except:
		logging.debug("Process GM message Failed")
		logging.debug(request.json)
		logging.error(sys.exc_info())
