#!/usr/bin/env python
import subprocess
import time
import json
import urllib
import pprint
import MySQLdb
import sys
db=MySQLdb.connect('localhost','auto','myvice12','main')
curs=db.cursor()
print("Getting Albany Weather")
c_index=0
city=['albany','salem','portland','newport','eugene']
while True:
#alerts
	
