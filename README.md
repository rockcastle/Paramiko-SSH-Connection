# Paramiko-SSH-Connection
Get some info from 3 different VMs using ssh connection with python 


Pereparation:


1- 3 different virtual boxes(A,B,C) on the same LAN

2- Each VM has installed ssh-server, one VM has installed all required python packages


3- Python Functions:
3.1- Pinging:
3.1.1- Program reads "ip" from config file to ping
3.1.2- ping each host 64bytes, 128bytes sizes 10 times for each size
3.1.3- calculate average time for pinging

3.2- SSH Connection:

3.2.1- SSH Connection from VM(A) to VM(B,C)

3.2.1.1- GET Storage capasity and free space 

3.2.1.2- GET RAM usage and free space 

3.2.1.3- GET CPU usegae at that time(once)

3.2.1.4- GET Interface ip and related MAC address

3.2.1.5- GET all these data write to file as json

3.2.1.6- Report all these info in a pdf file.

Requirements:
paramiko (pip install paramiko)
reportlab (pip install reportlab)
