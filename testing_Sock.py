#!/usr/bin/python
import thread,time,socket
UDP_IP = "10.0.0.2"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('',5005))
time.sleep(1)
# sock.connect((UDP_IP,UDP_PORT))

def send_packet():
	i=0
	while(True):
		i+=1
		time.sleep(1)
		message = "teststring to "+ UDP_IP + "at " + str(time.time()) 
		print(str(time.time())+" sent: "+message)
		sock.sendto(message,(UDP_IP,UDP_PORT))
		if (i==10):
			break

def receive_packet():
	i=0
	while(True):
		try:
			data = sock.recv(1024)
			if(len(data) != 0):
				print (str(time.time()) + " received: " + data)
				i+=1
				if (i==10):
					break
		except:
			continue

thread.start_new_thread(send_packet,())
thread.start_new_thread(receive_packet,())

time.sleep(20)