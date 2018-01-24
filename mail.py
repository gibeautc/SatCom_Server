#!/usr/bin/env python



import subprocess

def send_message(subject,msg):
    p=subprocess.Popen(["mail","-s",subject,"5419905349@vtext.com"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    p.communicate(msg)
    print(p.returncode)



if __name__=="__main__":
    send_message("Test","Hello")
