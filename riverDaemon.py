#!/usr/bin/env python

import time
import sys
import json
import MySQLdb
import urllib2




def get_example():
	print("Getting example file")
	#return json
	f=open('example','r')
	out=json.loads(f.read())
	return out

def parse_file(j):
	height=0.0
	flow=0.0
	print("Parsing file")
	try:
		value=j['value']
		ts=value['timeSeries']
		for val in ts:
			name=val['variable']['variableName']
			if 'flow' in name:
				flow=float(val['values'][0]['value'][0]['value'])
				print(flow)
			if 'height' in name:
				height=float(val['values'][0]['value'][0]['value'])
				print(flow)
	except:
		print("Error Parsing Data")
	#at this point we only want gauge height and flow rate
	#return [hight,flow]   ft,cfs
	




	return [height,flow]

def get_data(ID):
	print("Getting Current Stats for station: "+str(ID))
	
	response = urllib2.urlopen('https://waterservices.usgs.gov/nwis/iv/?format=json&sites='+str(ID)+'&parameterCd=00060,00065&siteStatus=all')
	html = response.read()
	out=json.loads(html)
	return out

def store(ID,data):
	#takes in int ID, and list data [height,flow]
	print("Added entry to database")
	

if __name__=="__main__":
	#example=get_example()
	#print(example)
	real=get_data('14181500')#hells canyon
	result=parse_file(real)
	print result



