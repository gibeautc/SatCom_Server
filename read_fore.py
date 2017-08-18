#!/usr/bin/env python
import MySQLdb
import sys
import datetime
import time


up=u"\u25B2"
down=u"\u25BC"
class bcolors:
	BLUE='\033[0;37;44m'
	ENDC='\033[0m'

def alert_scrub():
	months=['Error','January','February','March','April','May','June','July','August','September','October','November','December']
	curs.execute("select * from weather_alert where active=1")
	a=curs.fetchall()
	now=datetime.date.today()
	rem=0
	for alert in a:
		r=str(alert[3])
		s=r.split('on')
		d=s[1].split(" ")
		day=d[2].split(',')
		yr=d[3]
		for x in range(1,13):
			if months[x]==d[1]:
				m=x
				break
		if int(yr)<=now.year:
			if m<=now.month:
				if int(day[0])<now.day:
					rem+=1
					i=alert[8]
					print("ID: "+str(i))
					command='update weather_alert set active=0 where id='+str(i)+' limit 1'
					try:
						curs.execute(command)
						db.commit()
					except:
						print("Error Changing Entry: Rolling Back")
						db.rollback()
						print(sys.exc_info())
	print(str(rem)+" Expired")

class ten_day(object):
	def __init__(self,c):
		self.city=c
		self.high=[]
		self.low=[]
		self.wind=[]
		self.rain=[]
		self.snow=[]
		self.weather=[]
		self.alerts=[]
	def add_day(self,h,l,w,r,s,we):
		self.high.append(h)
		self.low.append(l)
		self.wind.append(w)
		self.rain.append(r)
		self.snow.append(s)
		self.weather.append(we)
	def Print(self):
		if len(self.high)!=10:
			print("Length error")
			print(self.high)
			return
		tabs=[]
		for l in self.weather:
			if len(l)<8:
				tabs.append("\t")
			elif len(l)<16:
				tabs.append("\t\t")
			else:
				tabs.append("\t\t\t")
		curs.execute("select * from weather_cur where city='"+self.city+"' and rec_date=current_date() order by id desc limit 1")
		full=curs.fetchall()
		s=full[0]		
		print("Weather for: "+self.city+"\t"+s[3]+"\tCurrent Temp: "+str(s[4])+" F\tWind: "+str(s[5])+" mph\tPressure trend: "+str(s[7])+"\tPrecip: "+str(s[8]))
		print("\nWeather"+"\t"+self.weather[0]+"\t"+self.weather[1]+"\t"+self.weather[2]+"\t"+self.weather[3]+"\t"+self.weather[4])
		temp=[]
		tmpw=[]
		tmpr=[]
		tmps=[]
		for x in range(9):
			th=self.trend(self.high)
			tl=self.trend(self.low)
			tw=self.trend(self.wind)
			tr=self.trend(self.rain)
			ts=self.trend(self.snow)
			tmpr.append(self.rain[x][:4]+tr)
			tmpw.append(self.wind[x][:4]+tw)	
			tmps.append(self.snow[x][:4]+ts)	
			if self.low[x]<=32:
				lowH=bcolors.BLUE+str(self.low[x])+bcolors.ENDC
			else:
				lowH=str(self.low[x])
			if self.high<=32:	
				highH=bcolors.BLUE+str(self.high[x])+bcolors.ENDC
			else:
				highH=str(self.high[x])
			temp.append(highH+th+"/"+lowH+tl)	
		print("Temp"+"\t"+temp[0]+tabs[0]+temp[1]+tabs[1]+temp[2]+tabs[2]+temp[3]+tabs[3]+temp[4])	
		print("Wind"+"\t"+tmpw[0]+tabs[0]+tmpw[1]+tabs[1]+tmpw[2]+tabs[2]+tmpw[3]+tabs[3]+tmpw[4])
		print("Rain"+"\t"+tmpr[0]+tabs[0]+tmpr[1]+tabs[1]+tmpr[2]+tabs[2]+tmpr[3]+tabs[3]+tmpr[4])
		print("Snow"+"\t"+tmps[0]+tabs[0]+tmps[1]+tabs[1]+tmps[2]+tabs[2]+tmps[3]+tabs[3]+tmps[4])
		for alert in self.alerts:
			print("ALERT: "+alert[4]+" Expires:"+alert[3]+" ID: "+str(alert[8]))
		print("\n\n")

	def trend(self,lst):
		trd=[]
		sm=0
		for n in range(len(lst)-1):
			x=float(lst[n])
			y=float(lst[n+1])
			trd.append(y-x)
			sm+=float(lst[n])
		s=0
		for n in trd:
			s+=n
		a=s/len(trd)
		#print("list sum: "+str(sm)+"\tAve: "+str(sm/len(lst)))
		#print("Trend Sum: "+str(s)+"\tAve: "+str(a))
		#print("")
		if abs(a)<.25:
			return ""
		if a<-.25:
			return down
		else:
			return up

def process_forcast(name):

	curs.execute("select * from weather_forecast where city='"+name+"' and fore_date>=current_date()")
	data=curs.fetchall()
	dates=[]
	forcast=[]
	for line in data:
		date=line[2]
		#will the dates always be in order????????
		if date not in dates:
			dates.append(date)
			t=[]
			forcast.append(t)
		i=dates.index(date)
		forcast[i].append(line)
	tenday=ten_day(forcast[0][0][16])
	for day in forcast:
		high=0
		low=0
		wind=0
		rain=0
		snow=0
		count=0
		for entry in day:
			high+=entry[3]
			low+=entry[4]
			rain+=entry[11]
			snow+=entry[14]
			wind+=entry[5]
			count+=1
			w=entry[15]
		high=high/count
		low=low/count
		rain=rain/count
		snow=snow/count
		wind=wind/count
		tenday.add_day(high,low,str(wind),str(rain),str(snow),w)
	curs.execute("select * from weather_alert where city='"+name+"' and active=1")
	a=curs.fetchall()
	for alert in a:
		if 'Craft' in alert[4]:
			continue
		tenday.alerts.append(alert)
	return tenday




db=MySQLdb.connect("localhost","auto","myvice12","main")
curs=db.cursor()
alert_scrub()


albany=process_forcast('albany')
albany.Print()

salem=process_forcast('salem')
salem.Print()

portland=process_forcast('portland')
portland.Print()


print("Closing Database and exiting")
db.close()
