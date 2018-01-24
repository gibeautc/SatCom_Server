#!/usr/bin/env python


import filelock
import os
import time
import subprocess
import logging as log
import mail

#add logging,
#add checks for if filename exists
#if pid file doesnt exist, maybe bacuse the process has not been run before

log.basicConfig(filename="/home/pi/logs/wd.log",level=log.INFO,format='%(asctime)s %(levelname)s : %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')
#lock.timeout=1
procList=[]
class proc:
    def __init__(self,fn):
        self.fileName=fn
        self.root=fn.split('/')
        self.root=self.root[len(self.root)-1]
        self.pidFile="/home/pi/logs/"+self.root+".pid"
        self.lock=None
    def start(self):
        if self.fileName=="" or self.pidFile=="":
            log.warning("Not setup correctly")
            log.warning("Filename:"+n.filename)
            log.warning("PID: "+n.pidFile)
            return
        self.lock=filelock.FileLock(self.pidFile)
        self.lock.timeout=1


def restart(n):
    log.warning("restarting "+n.fileName)
    f=open("/home/pi/logs/"+n.root+".error",'a')

    p=subprocess.Popen([n.fileName,],stdout=f,stderr=f)
    f.close()



f=open("/home/pi/SatCom_Server/wd.conf")
files=f.read().split("\n")
for line in files:
    if line=="" or line[0]=="#":
        continue
    if line[0]=="L":
        l=line.replace("L","")
        if l=="WARNING":
            log.level=log.WARNING
        if l=="INFO":
            log.level=log.INFO
        if l=="ERROR":
            log.level=log.ERROR

        continue
    tmp=proc(line)
    procList.append(tmp)
for n in procList:
    n.start()

log.info("Checking....")
for n in procList:
    try:
        n.lock.acquire()
        log.warning("Got In!")
        mail.send_message("WatchDog",n.pidFile)
        log.warning(n.pidFile)
        n.lock.release()
    except:
        log.info(n.root+" still Locked")
        continue
    restart(n)






