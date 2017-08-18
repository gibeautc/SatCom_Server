#!/usr/bin/env python

import os
import errno

blocked=[]
ip_list={}
user_name={}
FIFO='authpipe'

def logout(msg):
	l=open('blocklog','a+')
	l.write(str(msg))
	l.write('\n')
	l.close()

try:
	os.mkfifo(FIFO)
except OSError as oe:
	if oe.errno != errno.EEXIST:
		raise

#os.system("fail -f -n0 /var/log/auth.log > /home/pi/SatCom_server/authpipe &")
with open(FIFO,"r") as pipe:
	#os.system("tail -n0 /var/log/auth.log > /home/pi/SatCom_Server/authpipe")
	while True:
		data=pipe.readline()
		if data !="":
			if "Failed password" in data:
				elements=data.split(" ")
				if elements[10] not in ip_list:
					ip_list[elements[10]]=1
				else:
					ip_list[elements[10]]=ip_list[elements[10]]+1
				if elements[10] not in blocked:
					if ip_list[elements[10]]>10:
						#block them
						logout("Blocking: "+elements[10])
						os.system("sudo iptables -A INPUT -s "+elements[10]+" -j DROP")
						blocked.append(elements[10])	
				logout(elements)
	time.sleep(1)
