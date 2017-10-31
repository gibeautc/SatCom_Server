#!/usr/bin/env python
import time
import sys
import json

TEST=False



def parse_forcast(data):
	print("parsing data")
	data=json.loads(data)
	hourly=data['hourly_forecast']
	for e in hourly:
		day=e['FCTTIME']['mday']
		month=e['FCTIME']['mon']
		year=e['FCTIME']['year']
		hour=e['FCTIME']['hour']
		temp=e['temp']['english']
		sky=e['sky']
		condition=e['condition']
		wspd=e['wspd']['english']
		wdir=e['wdir']['degrees']
		wc=e['windchill']
		qpf=e['qpf']['english']
		snow=e['snow']['english']
		pres=e['mslp']['english']
		hum=e['humidity']
	if TEST:
		print("values")
	else:
		print("add to db")
	




def test():
	f=open('hourlyforcast_example','r')
	data=f.read()
	parse_forcast(data)




if len(sys.argv)>1:

	if 't' in sys.argv[1]:
		TEST=True
		test()
		exit()

while True:
	#main loop
	time.sleep(5)
