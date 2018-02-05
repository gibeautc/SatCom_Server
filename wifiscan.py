#!/usr/bin/env python



import MySQLdb
import subprocess
import sys
import time
db=MySQLdb.connect('localhost','root','aq12ws','wifi')
curs=db.cursor()

#sudo iwlist wlan0 scan

def add(name,level,sec,address):
    #server will have fixed lat/lon
    #check if address is in devices
    q="select 1 from devices where address=%s"
    curs.execute(q,[address,])
    d=curs.fetchall()
    print(d)
    if len(d)==0:
		print("Not in devices yet")
		insertDevice(name,sec,address)
    
    q="insert into records(tor,sig,lat,lon,address) values(Now(),%s,%s,%s,%s)"
    out=[str(level),"44.616042","-123.073326",address]
    print("adding")
    print(out)
    try:
        curs.execute(q,out)
        db.commit()
    except:
        db.rollback()
        print("Error Adding Entry")
        print(sys.exc_info())

def insertDevice(name,sec,address):
	q="insert into devices(address,name,sec) values(%s,%s,%s)"
	out=[str(address),str(name),str(sec)]
	print("adding New Device")
	print(out)
	try:
		curs.execute(q,out)
		db.commit()
	except:
		db.rollback()
		print("Error Adding Device")
		print(sys.exc_info())
def scan():
    out=subprocess.check_output(['sudo','iwlist','wlan0','scan'])
    cells=out.split("Cell")
    for c in cells:
        e=None
        q=None
        a=None
        s=None
        lines=c.split("\n")
        for line in lines:
            if "Address" in line:
                a=line.split("Address:")
                a=a[1]
                a=a.replace(" ","")
                #print(a)
            if "ESSID" in line:
                e=line.split(":")
                e=e[1]
                e=e.replace('"',"")
                #print("Name:"+e)
            if "Encryption key" in line:
                if ":on" in line:
                    s=0
                    #print("CLOSED")
                else:
                    s=1
                    #print("OPEN")
            if "Quality" in line:
                q=line.split("level=")
                q=q[1]
                q=int(q.replace("dBm",""))
                #print("Level:" +str(q))
        if a is None or e is None:
            continue
        if e is None:
            e=""
        if q is None:
            q=0
        if s is None:
            s=0
        if a is None:
            a="Unknown"
        if e.replace(" ","")=="":
            continue
        add(e,q,s,a)
        #print("")
    #print(len(cells))



if __name__=="__main__":
    scan()
