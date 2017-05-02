#!/usr/bin/python3.5
import subprocess
import threading
import re
import time
import sys
import logging
from subprocess import *

logging.basicConfig(filename="logging.txt", level=logging.DEBUG)


class myThread(threading.Thread):
    def __init__(self,threadID,name):
        try:
            threading.Thread.__init__(self)
            self.threadID =threadID
            self.threadName = name
            self.counter = 10
            self.size = [64,128] # default value 64
            logging.info("Thread is started successfully")
        except Exception as ex:
            logging.error("Thread can not started because of "+str(ex))

    def run(self):
        try:
            for i in self.size:
                threadLock.acquire()
                try2Ping(self.threadName,1,self.counter,i)
                threadLock.release()
            logging.info(self.threadName+" is started successfully at "+str(time.ctime()))

        except IOError as e:
            logging.error("Error to start thread :"+str(e))
            print("Error :" + str(e) )
            sys.exit(1)


def try2Ping(threadName,delay,counter,size):
    try:
        time.sleep(delay)
        p = subprocess.Popen(["ping",str(threadName),"-c",str(counter),"-s",str(size)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out,err = p.communicate()
        lns,er = out.decode(),err.decode()
        tp = 0.0; sy=0
        for i in lns.split(sep="\n"):
            i.strip()
            if re.search("bytes from",i):
                sy+=1;print(i)
                tm = i.split(" ")[6].split("=")[1]
                tp += float(tm)
            elif re.search("Destination Host Unreachable",i):
                sy+=1;print(i)
                logging.warning(threadName+" is unreachable at "+str(time.ctime())+" this time")
                pass
            else:
                pass
        print("SUM: " + str(tp)+"\n"+"Average: "+str(tp/sy) if sy!=0 else "SUM: 0.0\nAverage: 0.0")

    except IOError as ex:
        logging.error("Connection problem "+str(ex))
        print("Connection error :"+str(ex))
        sys.exit()

threadLock = threading.Lock()
def main():
    try:
        threads = []
        with open("config.txt",mode="r",encoding="utf-8") as fl:
            lines = fl.readlines()

            for i in range(len(lines)):
                locals()["thread"+str(i)] = myThread(i+1,lines[i].split(sep=",")[0])
                locals()["thread" + str(i)].start()
                threads.append(locals()["thread" + str(i)])
        #tüm threadlerin bitmesini beklemelk için
        for t in threads:
            t.join()
            print(t)
    except IOError as ex:
        logging.error("Error on threads operations "+str(ex))
        sys.exit()


if __name__=="__main__":
    main()

