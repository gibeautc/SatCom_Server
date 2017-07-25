#!/usr/bin/env python
import subprocess
import time
import json
import urllib
import pprint
import MySQLdb
import sys
import math
import binascii
db=MySQLdb.connect('localhost','auto','myvice12','main')
curs=db.cursor()
key=["35859b32434c5985","803ee257021d3c0e"]
kindex=0


def change_key():
	global kindex
	kindex+=1
	if kindex>1:
		kindex=0
	return
def bit_map(x,bits,in_min,in_max):
	out_min=0
	out_max=math.pow(2,bits)-1
	st='{0:0'+str(bits)+'b}'
	return st.format(int((x-in_min)*(out_max-out_min)/(in_max-in_min)+out_min))

def Get_weather(location):
	global key,kindex
	print("Getting Weather: "+location)
	url="http://api.wunderground.com/api/"+key[kindex]+"/hourly10day/q/"+location+".json"
	try:
		response=urllib.urlopen(url)
		data=json.loads(response.read())
	except:
		print("Error Getting Data")
		print(sys.exc_info())
		return
	forecast=data['hourly_forecast']
	cnt=0
	msg=""
	for h in forecast:
		windchill=h['windchill']['english']
		heatindex=h['heatindex']['english']
		mslp=h['mslp']['english']		#i dont know yet
		temp=h['temp']['english']
		dewpoint=h['dewpoint']['english']
		feelslike=h['feelslike']['english']
		wdir=h['wdir']['degrees']
		wspd=h['wspd']['english']
		qpf=h['qpf']['english']	#amount of precip
		fctcode=h['fctcode']	# code that coresponds to an icon for weather
		sky=h['sky']	#lower is more clear sky
		pop=h['pop']
		mon=h['FCTTIME']['mon']
		day=h['FCTTIME']['mday']
		hour=h['FCTTIME']['hour']
		year=h['FCTTIME']['year']
		wday=h['FCTTIME']['weekday_name_unlang']
		if int(hour)>5:
			if int(hour)<19:
				print(str(day)+":"+str(hour)+": "+str(sky))	
		#msg text will be binary at this point   each hour will be 5 bits of sky coverage(0-100%), 5 bits of precip(0-2in), 5 bits for wind (0-100mph).
		# The remaining bit will be 0 for rain, 1 for snow
		#The string will contain 25 hours of data, starting at the current hour.
		temp=bit_map(int(temp),5,15,115)
		sky=bit_map(int(sky),4,0,100)
		wind=bit_map(int(wspd),4,0,75)
		precip=bit_map(float(qpf),3,0,1)
		msg=msg+temp+sky+wind+precip
		msg_int=int(msg,2)
		msg_ascii=binascii.b2a_base64(msg)
		#print(msg_ascii)
		#print(sys.getsizeof(msg_int))
		#hmsg=hex(int(msg,2))
		#hmsg=hmsg[2:-1]
		#print(hmsg)
		#n=int(hmsg,16)
		#print(msg)
		#print("")
		#print("Len(bin):"+str(len(msg)))
		#print("Len:"+str(len(hmsg)))
		#print("Len(int):"+str(sys.getsizeof(n)))
		#print("")
		#only take first 25
		cnt=cnt+1
		#if cnt>24:
	#		break#only pulling the first 25
		#Build a message with 



		#db_out=[location,str(windchill),str(heatindex),str(mslp),str(temp),str(dewpoint),str(feelslike),str(wdir),str(wspd),str(qpf),str(fctcode),str(sky),str(pop),str(mon),str(day),str(hour),str(year),str(wday)]
		#try:
	#		curs.execute('insert into SatWeather values(current_date(),now(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',db_out)
	#		db.commit()
	#	except:
	#		print("Error: Rolling Back")
	#		db.rollback()
	#		print(sys.exc_info())

		
Get_weather("44.615339,-123.07098")
#print(bit_map(115,5,15,115))	
