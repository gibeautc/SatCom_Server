#!/usr/bin/env python
import sys
import json
import datetime
import os
import logging as log
import urllib2
from bitarray import bitarray
import binascii
import struct
TEST=True

WUGBase='http://api.wunderground.com/api/35859b32434c5985/'

alert_types=['HUR','TOR','TOW','WRN','SEW','WIN',
			'FLO','WAT','WND','SVR','HEA','HEA','FOG',
			'FOG','SPE','FIR','VOL','HWW','REC','REP','PUB']

alert_strings=['Hurricane Local Statement','Tornado Warning',
				'Tornado Watch','Severe Thunderstorm Warning',
				'Severe Thunderstorm Watch','Winter Weather Advisory',
				'Flood Warning','Flood Watch / Statement',
				'High Wind Advisory','Severe Weather Statement',
				'Heat Advisory','Dense Fog Advisory',
				'Special Weather Statement','Fire Weather Advisory',
				'Volcanic Activity Statement','Hurricane Wind Warning',
				'Record Set','Public Reports',
				'Public Information Statement']


def _webResponse(url):
	try:
		response=urllib2.urlopen(url)
	except:
		log.error("Response Fail")
		log.error(url)
		log.error(sys.exc_info())
		return None
	try:
		html=response.read()
	except:
		log.error("Failed to read response")
		log.error(url)
		return None
	try:
		jsonData=json.loads(html)
	except:
		log.error("Failed to get JSON from response")
		log.error(url)
		return None
	return jsonData
	

def get_river_data(ID):
	log.info("Getting Current Stats for station: "+str(ID))
	try:
		r=_webResponse('https://waterservices.usgs.gov/nwis/iv/?format=json&sites='+str(ID)+'&parameterCd=00060,00065&siteStatus=all')
		if r is None:
			log.warning("river web response=None")
			return None
		height=0.0
		flow=0.0
		try:
			value=r['value']
			ts=value['timeSeries']
			for val in ts:
				name=val['variable']['variableName']
				if 'flow' in name:
					flow=float(val['values'][0]['value'][0]['value'])
				if 'height' in name:
					height=float(val['values'][0]['value'][0]['value'])
		except:
			log.error("Error Parsing Data")
			return None
		ret={}
		ret['height']=height
		ret['flow']=flow
		return [height,flow]   #ft,cfs
	except:
		log.error("Failed to get River data:"+str(ID))
		log.error(sys.exc_info())
		return None
		
def get_forecast(lat,lon):
	mode="hour"
	log.info("Getting forcast")
	location=str(lat)+","+str(lon)+".json"
	url=WUGBase+"/hourly10day/q/"+location
	try:
		data=_webResponse(url)
		if data is None:
			return
	except:
		log.error("Error Getting Forecast from web")
		log.error(response.read())
		log.error(sys.exc_info())
		return
	hourly=data['hourly_forecast']
	returnDict={}
	cnt=0
	day=-1
	lastDay=-1
	high=-100
	low=200
	wind=0
	aveCnt=0
	rain=0
	snow=0
	sky=0
	Dcnt=0
	for e in hourly:
		if Dcnt>4:
			break
		day=e['FCTTIME']['mday']
		if day==-1:
			lastDay=e['FCTTIME']['mday']
			day=lastDay
		if lastDay!=day:
			lastDay=day
			print("New Day")
			print("HIGH:"+str(high))
			print("LOW:"+str(low))
			print("Wind"+str(wind))
			print("Rain"+str(rain))
			print("Sky"+str(sky))
			if mode=='day':
				entDict={}
				entDict['day']=e['FCTTIME']['mday']
				entDict['high']=high
				entDict['low']=low
				entDict['sky']=sky/aveCnt
				entDict['wind']=wind/aveCnt
				entDict['rain']=rain
				entDict['snow']=snow
				returnDict['D'+str(Dcnt)]=entDict
				Dcnt=Dcnt+1
			high=-100
			low=200
			wind=0
			aveCnt=0
			rain=0
			snow=0
			sky=0
		t=float(e['temp']['english'])
		if t>high:
			high=t
			print("new high!:"+str(high))
		if t<low:
			low=t
			print("new low!:"+str(low))
		wind=wind+int(e['wspd']['english'])
		rain=rain+float(e['qpf']['english'])
		snow=snow+float(e['snow']['english'])
		sky=sky+int(e['sky'])
		aveCnt=aveCnt+1
		if mode=="hour":
			entDict={}
			entDict['time']=e['FCTTIME']['epoch']
			entDict['temp']=t
			entDict['sky']=e['sky']
			entDict['wind']=e['wspd']['english']
			entDict['rain']=e['qpf']['english']
			entDict['snow']=e['snow']['english']
			returnDict['H'+str(cnt)]=entDict
			cnt=cnt+1
			lastDay=e['FCTTIME']['mday']
		if cnt>=20:
			mode="day"
	return returnDict
	

def get_alert(lat,lon):
	log.info("Getting Alert")
	location=str(lat)+","+str(lon)+".json"
	url=WUGBase+'/alerts/q/'+location
	try:
		data=_webResponse(url)
		if data is None:
			return
	except:
		log.error("Error Getting Alerts from web")
		log.error(response.read())
		log.error(sys.exc_info())
		return
	log.info("Parsing Alert for ")
	alerts=data['alerts']
	return alerts

def mapRange(x,in_min,in_max,out_min,out_max):
	val= (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
	if int(val)>out_max:
		return out_max
	return int(val)

def mapRangeF(x,in_min,in_max,out_min,out_max):
	val= (float(x) - float(in_min)) * (float(out_max) - float(out_min)) / (float(in_max) - float(in_min)) + float(out_min)
	if int(val)>out_max:
		return out_max
	return val

def getFullData(lat,lon):
	finalData=json.loads("{}")
	finalData['alerts']=get_alert(lat,lon)
	finalData['weather']=get_forecast(lat,lon)
	finalData['river']=get_river_data(13317000)
	return finalData
	
def convertToBytes(data):
	#each hour is 20 bits, and there are 20 of them   so 400 bits 
	#each day is 25 bits, and there is 5 of them, so 125 bits
	#total for weather is 525 bits = 66 Bytes
	returnData=bitarray()
	for h in range(20):
		hour=data['weather']['H'+str(h)]
		temp=int(float(hour['temp']))
		sky=int(hour['sky'])
		rain=float(hour['rain'])
		wind=int(float(hour['wind']))
		temp=mapRange(temp,-20,120,0,28)
		sky=mapRange(sky,0,100,0,25)
		rain=mapRange(rain,0,2,0,20)
		wind=mapRange(wind,0,75,0,15)
		temp=bitarray(format(temp,'05b'))
		sky=bitarray(format(sky,'05b'))
		rain=bitarray(format(rain,'05b'))
		wind=bitarray(format(wind,'04b'))
		returnData.extend(temp)
		returnData.extend(sky)
		returnData.extend(wind)
		#at some point add in the snow, which would make this next line True, but trying to make it simple for now
		returnData.append(False)
		returnData.extend(rain)
		print("Hour: "+str(h)+"\t\tCurrent Length of Data: "+str(len(returnData)))
	for d in range(5):
		#{'sky': 78, 'snow': 0.0, 'rain': 0.0, 'high': u'76.1', 'low': 200, 'day': u'14', 'wind': 3}
		hour=data['weather']['D'+str(d)]
		
		high=int(float(hour['high']))
		low=int(float(hour['low']))
		print("LOW:"+str(low))
		print("HIGH:"+str(high))
		sky=int(hour['sky'])
		rain=float(hour['rain'])
		print("Rain Raw: "+str(rain))
		wind=int(float(hour['wind']))
		
		high=mapRange(high,-20,120,0,28)
		low=mapRange(low,-20,120,0,28)
		sky=mapRange(sky,0,100,0,25)
		rain=mapRange(rain,0,2,0,20)
		print("Rain Enum: "+str(rain))
		wind=mapRange(wind,0,75,0,15)
		
		high=bitarray(format(high,'05b'))
		low=bitarray(format(low,'05b'))
		sky=bitarray(format(sky,'05b'))
		rain=bitarray(format(rain,'05b'))
		print("Rain bits: "+str(rain))
		wind=bitarray(format(wind,'04b'))
		print(len(high))
		print(len(low))
		print(len(sky))
		print(len(rain))
		print(len(wind))
		returnData.extend(high)
		returnData.extend(low)
		returnData.extend(sky)
		returnData.extend(wind)
		#at some point add in the snow, which would make this next line True, but trying to make it simple for now
		returnData.append(False)
		returnData.extend(rain)
		print("Day: "+str(d)+"\t\tCurrent Length of Data: "+str(len(returnData)))
	river=data['river']
	riverH=''.join(bin(ord(c)).replace('0b', '').rjust(8, '0') for c in struct.pack('!f', river[0]))
	riverF=''.join(bin(ord(c)).replace('0b', '').rjust(8, '0') for c in struct.pack('!f', river[1]))
	print(riverH)
	print(riverF)
	returnData.extend(riverH)
	returnData.extend(riverF)
	return binascii.hexlify(returnData)
def convertFromBytes(data):
	#write this here for testing, and then can move it over to the Client side
	cnt=0
	bitA=bitarray()
	bitA.frombytes(data.decode('hex'))
	bitA=bitA[:-3]  #take off 3 filler bits
	#print(bitA)
	#print(len(bitA))
	#each Hour is 20 bits
	for h in range(20):
		hourbits=bitA[cnt:cnt+20]
		cnt=cnt+20
		#temp,sky,wind,precip type,precip (rain)
		#type is one bit, wind is 4, all others are 5
		print(hourbits)
		temp=int(hourbits[:5].to01(),2)
		sky=int(hourbits[5:10].to01(),2)
		wind=int(hourbits[10:14].to01(),2)
		rain=int(hourbits[-5:].to01(),2)
		
		temp=mapRange(temp,0,28,-20,120)
		sky=mapRange(sky,0,25,0,100)
		wind=mapRange(wind,0,15,0,75)
		rain=mapRangeF(rain,0,20,0,2)
		print("Hour: "+str(h))
		print("Temp: "+str(temp))
		print("Sky: "+str(sky))
		print("Wind: "+str(wind))
		print("Rain: "+str(rain))
		print("")
	#each day is 25 bits starting at 400
	for d in range(5):
		#high,low,sky,wind,precip type,precip (rain)
		#type is one bit, wind is 4, all others are 5
		daybits=bitA[cnt:cnt+25]
		print(daybits)
		cnt=cnt+25
		high=int(daybits[:5].to01(),2)
		low=int(daybits[5:10].to01(),2)
		sky=int(daybits[10:15].to01(),2)
		wind=int(daybits[15:19].to01(),2)
		rain=int(daybits[-5:].to01(),2)
		
		high=mapRange(high,0,28,-20,120)
		low=mapRange(low,0,28,-20,120)
		sky=mapRange(sky,0,25,0,100)
		wind=mapRange(wind,0,15,0,75)
		rain=mapRangeF(rain,0,20,0,2)
		print("Day: "+str(d))
		print("High: "+str(high))
		print("Low: "+str(low))
		print("Sky: "+str(sky))
		print("Wind: "+str(wind))
		print("Rain: "+str(rain))
		print("")
	#this brings us to bit 525
	riverHbits=bitA[cnt:cnt+8*4]
	cnt=cnt+(8*4)
	riverFbits=bitA[cnt:]
	print(riverHbits)
	print(riverFbits)

def getData(lat,lon):
	d=getFullData(lat,lon)
	print(d)
	print(len(d['weather']))
	b=convertToBytes(d)
	print(b)
	print(len(b))
	return b
if __name__=="__main__":
	lat=44.6158599
	lon=-123.073257
	g=getData(lat,lon)
	#convertFromBytes('a9400a9840a1840a0c40a080098c0098c0098c009900091c0091c009300193000938008b80093c0094c0094c009cc409cc40a45c00ca4d102527001293800949e0020b5eb85230114002')
	convertFromBytes(g)
