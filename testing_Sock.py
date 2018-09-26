#!/usr/bin/python
import thread,time,socket
UDP_IP = "127.0.0.2"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1',5005))

def send_packet():
	while(True):
		time.sleep(1)
		message = "teststring to "+ UDP_IP + "at " + str(time.time()) 
		sock.sendto(message,(UDP_IP,UDP_PORT))

def receive_packet():
	while(True):
		try:
			data = sock.recv(1024)
			if(len(data) != 0):
				print (str(time.time()) + " received: " + data)
		except:
			continue

thread.start_new_thread(send_packet,())
thread.start_new_thread(receive_packet,())

time.sleep(10)