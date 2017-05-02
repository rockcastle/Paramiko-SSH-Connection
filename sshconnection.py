#!/usr/bin/python3.5
from itertools import count

import paramiko
import logging
import sys
import time
import re
import json
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

logging.basicConfig(filename="sshconnLogs.txt",level=logging.DEBUG)
jobs2do = ["df -h","free -m","top -bn1 | grep Cpu","ifconfig"]
jdata=''
hjdata={"pdf_filename":"TestResult.pdf",
                    "font_name":"Courier","font_size":12,"header":"SSH Connection test",
                    "footer":"SSH Connection test","lines":"get lines from json"}

class sshConnection():
    def __init__(self,host,uname,passwd):
        try:
            self.host = host
            self.uname = uname
            self.passwd = passwd
            hjdata["Host " + self.host] = {"HostIP": self.host, "UserName": self.uname, "Password": self.passwd}
        except Exception as ex:
            logging.error("SSH command is not right for "+str(host)+" "+str(ex)+" on "+time.ctime())
            self.sshclient.close()
            sys.exit()

    def run(self):
        try:
            self.sshclient = paramiko.SSHClient()
            self.sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.sshclient.connect(hostname=self.host, username=self.uname, password=self.passwd)
            logging.info("Connection established successfully to "+str(self.host)+" on " + time.ctime())
            hjdata["Host " + self.host]["SSH info"] = {"SSHConnection":"Established"}
            for i in jobs2do:
                if self.sshclient:
                    stdin, stdout, stderr = self.sshclient.exec_command(i)
                    sshConnection.getInf(self,i,*stdout)
                    time.sleep(1)
            self.sshclient.close()
        except IOError as ex:
            logging.error(str(ex)+" on "+time.ctime())
            hjdata["Host " + self.host]["SSH info"] = {"SSHConnection":"Not Established"}
            self.sshclient.close()

    def getInf(self,op,*val):
        try:
            self.val = list(val) #stdout
            self.op = op # which command to send client
            mega = re.compile("M")
            giga = re.compile("G")
            kilo = re.compile("K")
            if re.search(jobs2do[0],self.op): #self.op == jobs2do[0]: # which commancd is working
                hd = []
                for i in (self.val):
                    if re.search("\d+\w",i):
                        #print(i.split(" "))
                        for k in i.split(" "):#Search lines for numbers to get HDD values like "/tmp 454 12 456"
                            r1 = re.search("^\d.\w",k)
                            r2 = re.fullmatch("0",k)
                            if r1 or r2: #start with numbers ncluding one special caracter (,) and ends one word
                                hd.append(k)
                            else:
                                pass
                    else:
                        pass
                # Total Size için
                self.ts=0.0# As GigaByte
                self.avs=0.0
                self.used=0.0
                self.rm0='';self.rm1='';self.rm2='';self.hRAM=[];self.hCPU=[]
                for m in range(0,len(hd),3):
                    if re.search(mega,hd[m]): # search for MByte values
                        if re.search(",",hd[m].split("M")[0]): # search for commas(","), if then replace it with dots(.) for math calculations
                            self.ts += round(float(re.sub(",",".",hd[m].split("M")[0]))/1024,3)
                        else:
                            self.ts += round(float(hd[m].split("M")[0])/1024,3)
                    elif re.search(giga,hd[m]):
                        if re.search(",",hd[m].split("G")[0]):
                            self.ts += round(float(re.sub(",", ".", hd[m].split("G")[0])), 3)
                        else:
                            self.ts += round(float(hd[m].split("G")[0]),3)
                        #print(hd[m].split("G")[0])
                    elif re.search(kilo,hd[m]) and re.sub(",",".",hd[m]):
                        if re.search(",",hd[m].split("K")[0]):
                            self.ts += round(float(re.sub(",", ".", hd[m].split("K")[0])) / (1024*1024),3)
                        else:
                            self.ts += round(float(hd[m].split("K")[0])/(1024*1024),3)
                        #print(hd[m].split("K")[0])
                    else:
                        self.ts += 0.0
                        pass
                print("\nHDD info\n")
                print("\tTotal size of HDD:\t "+str(round(self.ts,3))+"GB")
                logging.info("Total size of HDD: "+str(round(self.ts,3))+"GB")

                #Used size of HDD
                for u in range(1,len(hd),3):
                    if re.search(mega,hd[u]):
                        if re.search(",",hd[u].split("M")[0]):
                            self.used += round(float(re.sub(",",".",hd[u].split("M")[0]))/1024,3)
                        else:
                            self.used += round(float(hd[u].split("M")[0])/1024,3)
                    elif re.search(giga, hd[u]):
                        if re.search(",", hd[u].split("G")[0]):
                            self.used += round(float(re.sub(",", ".", hd[u].split("G")[0])), 3)
                        else:
                            self.used += round(float(hd[u].split("G")[0]), 3)
                    elif re.search(kilo, hd[u]) and re.sub(",", ".", hd[u]):
                        if re.search(",", hd[u].split("K")[0]):
                            self.used += round(float(re.sub(",", ".", hd[u].split("K")[0])) / (1024 * 1024), 3)
                        else:
                            self.used += round(float(hd[u].split("K")[0]) / (1024 * 1024), 3)
                    else:
                        self.used += 0.0
                        pass
                print("\tUsed size of HDD:\t " + str(round(self.used, 3)) + "GB")
                #hjdata["Host " + self.host]["HDD info"] = {"Used size of HDD":str(round(self.used, 3)) + "GB"}
                logging.info("Used size of HDD: " + str(round(self.used, 3)) + "GB")

                # Available size of HDD
                for av in range(2,len(hd),3):
                    #print(hd[av])
                    if re.search(mega, hd[av]):
                        if re.search(",", hd[av].split("M")[0]):
                            self.avs += round(float(re.sub(",", ".", hd[av].split("M")[0])) / 1024, 3)
                        else:
                            self.avs += round(float(hd[av].split("M")[0]) / 1024, 3)
                    elif re.search(giga, hd[av]):
                        if re.search(",", hd[av].split("G")[0]):
                            self.avs += round(float(re.sub(",", ".", hd[av].split("G")[0])), 3)
                        else:
                            self.avs += round(float(hd[av].split("G")[0]), 3)
                    elif re.search(kilo, hd[av]) and re.sub(",", ".", hd[av]):
                        if re.search(",", hd[av].split("K")[0]):
                            self.avs += round(float(re.sub(",", ".", hd[av].split("K")[0])) / (1024 * 1024), 3)
                        else:
                            self.avs += round(float(hd[av].split("K")[0]) / (1024 * 1024), 3)
                    else:
                        self.avs += 0.0
                        # print("Nothing...")
                        pass
                print("\tAvailable size of HDD:\t " + str(round(self.avs, 3)) + "GB")
                logging.info("Available size of HDD: " + str(round(self.avs, 3)) + "GB")

                hjdata["Host " + self.host]["HDD info"] = {"Total size of HDD":str(round(self.ts,3))+"GB","Used size of HDD":str(round(self.used, 3)) + "GB",
                                                           "Available size of HDD": str(round(self.avs, 3)) + "GB"}

            elif re.search(jobs2do[1],self.op): # Get RAM info
                for r in (self.val):
                    if re.search("\d+\w", r):#Get RAM values from line
                        if re.search("Mem",r):
                            for rm in r.split(" "):
                                r1 = re.search("\d+", rm)
                                if r1:  # start with numbers including one special caracter (,) and ends one word
                                    self.hRAM.append(rm)
                                else:
                                    pass
                    else:
                        pass
                self.rm0=self.hRAM[0]
                self.rm1 = self.hRAM[1]
                self.rm2 = self.hRAM[2]
                print("\nRAM info\n")
                print("\tTotal RAM: "+str(self.rm0))
                print("\tUsed RAM: "+str(self.rm1))
                print("\tFree RAM: "+str(self.rm2))
                hjdata["Host " + self.host]["RAM info"] ={"Total size of RAM": str(self.rm0), "Used size of RAM": str(self.rm1),"Free size of RAM": str(self.rm2)}

            elif re.search(jobs2do[2],self.op):#Get CPU usage
                for c in (self.val):
                    cp = c.split(" ")
                    print("\nCPU info\n")
                    for cu in range(0,len(cp)):
                        if re.search("us",cp[cu]):
                            print("\tRunning user space processes percentage (us):\t "+str(cp[cu-1]))
                            self.hCPU.append(cp[cu-1])
                        elif re.search("sy",cp[cu]):
                            print("\tRunning kernel :\t " + str(cp[cu - 1]))
                            self.hCPU.append(cp[cu - 1])
                        elif re.search("id",cp[cu]):
                            print("\tCPU free(idle) :\t " + str(cp[cu - 1]))
                            self.hCPU.append(cp[cu - 1])
                        elif re.search("ni",cp[cu]):
                            print("\tHow much time CPU spent running user space processes (ni) :\t" + str(cp[cu - 1]))
                            self.hCPU.append(cp[cu - 1])
                        elif re.search("wa",cp[cu]):
                            print("\tIntpu Output Operations (wa) :\t" + str(cp[cu - 1]))
                            self.hCPU.append(cp[cu - 1])
                        else:
                            pass
                #print(self.hCPU)
                hjdata["Host " + self.host]["CPU info"] = {"UserSpaceProcesses(us)":str(self.hCPU[0]),"Kernel(sy)": str(self.hCPU[1]),"idle(id)": str(self.hCPU[3]),
                                                           "ni":str(self.hCPU[2]),"InputOutpuOperations(wa)": str(self.hCPU[4])}
            elif re.search(jobs2do[3],self.op):#Get MAC Address of interface
                s=0
                #print(len(self.val))
                #print(self.val[0])
                for eth in self.val:
                    if re.search("\w+:\s",eth):
                        s+=1
                ethsay = round(len(self.val) / s)# ilk değer 8 ilke değer içinde yoksa +8 eklenip diğer interface kontrol ediliyor
                for say in range(ethsay):
                    #print(self.val[say])
                    if re.search(self.host,self.val[say]):
                        print("\n"+str(self.val[say]).strip()+" isa\n")
                        say+=1
                        if re.search("ether",self.val[say]):
                            print(self.val[say])
                            mac=self.val[say].split(" ")
                            print(mac);say+=1
                            for n in mac:
                                if re.search("^\d\d:\d",self.m):
                                    self.m = n
                                    print("\tMAC address: \t"+str(self.m)+"\n")
                                    #hjdata["Host " + self.host]["MAC address"] = {self.host + " mac": str(m)}
                                else:
                                    pass
                        else:
                            say+=1
                            mac = self.val[say].strip().split(" ")
                            for n in mac:

                                if re.search("^\d\d:\d",n):
                                    self.m = n
                                    #hjdata["Host " + self.host]["MAC address"] = {self.host + " mac": str(self.m)}
                                    print("\tMAC address: \t"+str(self.m)+"\n")
                                else:
                                    pass
                    else:
                        ethsay += 8
                        pass
                hjdata["Host " + self.host]["MAC address"] = {str(self.host):str(self.m)}
            else:
                logging.info("Cannot get MAC address")
                pass
        except Exception as ex:
            logging.error("Output error "+str(ex))
            sys.exit()

    def json2pdf(*json_data):
        try:
            data = json.loads(*json_data)
            pdf_filename = data["pdf_filename"]
            font_name = data["font_name"]
            font_size = data["font_size"]
            print(data)

            c = canvas.Canvas(pdf_filename)
            c.setTitle("SSH Connection Test Automation")
            c.setAuthor("Isa Bostan\nisabostan@gmail.com")
            c.setFont(font_name,size=18)
            c.drawCentredString(300,810,"SSH Connection Test Automation")
            c.setFont(font_name, size=8)
            c.drawCentredString(300,790,"Isa Bostan")
            img = "mimosa.png"
            c.drawString(20,770,"Test 1: Config dosyasindaki ip adreslerine ssh ile baglanti kurulacak")
            c.drawString(20,760, "Test 2: PC lerden CPU, RAM, HDD ve MAC adres degerlerinin alinip raporlanmasi")
            y=740
            for i in data:
                #print(data[i])
                if re.search("host", i, flags=re.IGNORECASE):
                    ipadr = ""
                    if data[i]["SSH info"]["SSHConnection"]=="Established":
                        print(data[i]["HostIP"])
                        #for l in data[i]:
                        #    print(l)
                        #print("Connected")

                        if not re.fullmatch(ipadr,data[i]["HostIP"]):
                            y-=8
                            c.drawString(30,y,i+" ssh connection estanblished")
                            y-=12
                            c.drawString(50, y, "CPU info")
                            y -= 10
                            c.drawString(70, y, "Running user space processes(us): " + data[i]["CPU info"]["UserSpaceProcesses(us)"])
                            y -= 12
                            c.drawString(70, y, "Running kernel(sy): " + data[i]["CPU info"]["Kernel(sy)"])
                            y -= 12
                            c.drawString(70, y, "How much time CPU spent running user space processes: " + data[i]["CPU info"]["ni"])
                            y -= 12
                            c.drawString(70, y, "CPU free(idle): " + data[i]["CPU info"]["idle(id)"])
                            y -= 12
                            c.drawString(70, y, "Intpu Output Operations (wa): " + data[i]["CPU info"]["InputOutpuOperations(wa)"])
                            y -= 12
                            c.drawString(50, y, "HDD info")
                            y -= 10
                            c.drawString(70, y,"Total size of HDD: " + data[i]["HDD info"]["Total size of HDD"])
                            y-= 12
                            c.drawString(70, y, "Used size of HDD: " + data[i]["HDD info"]["Used size of HDD"])
                            y -= 12
                            c.drawString(70,y,"Available size of HDD: "+data[i]["HDD info"]["Available size of HDD"])
                            y-=12
                            c.drawString(50, y, "RAM info")
                            y -= 10
                            c.drawString(70, y, "Total RAM: " + data[i]["RAM info"]["Total size of RAM"])
                            y -= 12
                            c.drawString(70, y, "Used RAM: " + data[i]["RAM info"]["Used size of RAM"])
                            y -= 12
                            c.drawString(70, y,"Free RAM: " + data[i]["RAM info"]["Free size of RAM"])
                            y -= 12
                            c.drawString(50, y, "MAC address")
                            y -= 10
                            c.drawString(70, y, "MAC address: " + data[i]["MAC address"][data[i]["HostIP"]])
                            y -= 12
                        else:
                            c.drawString(30, y, i + " ssh connection estanblished")
                        ipadr = data[i]["HostIP"]
                    else:
                        y-=12
                        c.drawString(30, y, i + " ssh connection not estanblished")
                        y-=12
                        print("Not connected, check your settings")
                        pass

            c.drawImage(img, 300, 120)
            c.showPage()
            c.save()
        except IOError as ioe:
            logging.error("Error while writing to pdf "+str(ioe))
            sys.exit(1)
def main():
    try:
        with open("config.txt",mode="r",encoding="utf-8") as f:
            for hosts in f:
                host = hosts.split(",")
                print(host)
                sshConnection(host[0].strip(),host[1].strip(),host[2].strip()).run()
        data = json.dumps(hjdata, ensure_ascii=False, sort_keys=True)
        sshConnection.json2pdf(data)
    except Exception as ex:
        logging.error("Cannot read hosts from file "+str(ex))
        sys.exit()


if __name__=="__main__":
    main()