#The following things need to be multi-threaded
# 2. from_physical_layer function of data layer
# 3. from_network_layer function of data layer

import time
import socket
from random import randint
from threading import Lock, Thread

lock = Lock()
#this is set by data layer
NETWORK_LAYER_ENABLED = False
#this is set by network layer
NETWORK_LAYER_READY = False

MAX_PACKET_LENGTH = 4096

PACKET_SEQUENCE = 0

HOST_ID = 0

TOTAL_HEADER_LENGTH = 32

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('',5005))

class Packet:
	def __init__(self):
		global PACKET_SEQUENCE
		self.seq = PACKET_SEQUENCE
		self.host = HOST_ID
		PACKET_SEQUENCE+=1
		payload_string = "datadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadata"
		payload_length = randint()%MAX_PACKET_LENGTH
		self.info = payload_string[:payload_length]

class NetworkLayer:
	def send_packet(self):
		if (NETWORK_LAYER_ENABLED):
			a = Packet()
			return a

	def receive_packet(self, packet):
		f=open("packet_dump"+str(HOST_ID)+".txt","a+")
		f.write("%f\t%d\n" %(str(time.time(),len(str(packet.seq)) + len(str(packet.host)) + len(packet.info))))
		f.close()

#global network layer
network_layer = NetworkLayer()

class Frame:
	def __init__(self,frame_kind,seq_nr,ack_nr,info):
		self.seq = seq_nr
		self.ack = ack_nr
		#info is of type Packet
		self.info = info

class DataLinkLayer:
	def __init__(self, MAX_SEQ, TIME_FOR_ACK):
		#Initializations
		self.next_frame_to_send = 0
		self.ack_expected = 0
		self.frame_expected = 0
		#buffer contains packets, a maximum of MAX_SEQ
		self.buffer = [Packet()]*(MAX_SEQ + 1) # why packet here!
		self.nbuffered = 0
		self.event = None
		self.network_layer_enabled = False
		self.MAX_SEQ = MAX_SEQ
		#timer times the last expected ack
		self.timer = 0
		self.TIME_FOR_ACK = TIME_FOR_ACK
		self.frame_available = False

	def enable_network_layer():
		NETWORK_LAYER_ENABLED = True

	def disable_network_layer():
		NETWORK_LAYER_ENABLED = False

	def start_timer(frame_nr):
		self.timer = time.time()

	def stop_timer(ack_nr):
		self.timer = 0

	def time_over():
		return(time.time() - self.timer) > self.TIME_FOR_ACK

	def to_physical_layer(frame):
		packet = frame.info
		packet_str = str(packet.seq) + "_" + str(packet.host) + "_" + str(packet.info)
		frame_str = str(frame.seq) + "_" +  str(frame.ack)
		message = packet_str + frame_str 
		check_sum_string = gen_check_sum(message)
		message+="_"+check_sum_string
		sock.sendto(message,(UDP_IP,UDP_PORT))
	
	def convertStrToFrame(string):
		l = string.split("_")
		p = Packet()
		f = Frame()
		p.seq = int(l[0])
		p.host = int(l[1])
		p.info = l[2]
		f.seq = int(l[3])
		f.ack = int(l[4])
		f.checksum = l[5]
		f.info = p
		return f

	#returns false if frame has not arrived
	#if frame has arrived, set frame_available to true
	def from_physical_layer():
		while(True):
			try:
				data = sock.recv(MAX_PACKET_LENGTH)
			except:
				continue
			frame = self.convertStrToFrame(data)
			self.frame_available = True
			return frame

	def send_data(frame_nr,frame_expected):
		s = Frame();
		s.info = self.buffer[frame_nr]
		s.seq = frame_nr
		s.ack = (frame_expected + self.MAX_SEQ)%(self.MAX_SEQ + 1)
		self.to_physical_layer(s)
		start_timer()

	def to_network_layer(packet):
		network_layer.receive_packet(packet)

	def from_network_layer():
		while(True):
			if (int(time.time()*1000)%2 == 1):
				NETWORK_LAYER_READY = True
			else:
				NETWORK_LAYER_READY = False
			if(NETWORK_LAYER_READY and NETWORK_LAYER_ENABLED):
				packet = network_layer.send_packet()
				return packet

	def gen_check_sum(frame_string):
		return str(hash(frame_string)%1024)

	def check_sum(frame):
		frame_string = str(frame.info.seq)+"_"+str(frame.info.host)+"_"+str(frame.info.info)+"_"+str(frame.seq) + "_" + str(frame.ack)
		if (gen_check_sum(frame_string)==frame.check_sum):
			return True
		else:
			return False

	def GBN_protocol():
		self.enable_network_layer();
		while(True):
			#set event here
			if(NETWORK_LAYER_READY):
				self.event = "network_layer_ready"
			elif(self.frame_available):
				self.event = "frame_arrival"
			elif(self.time_over()):
				self.event = "timeout"

			#handling packets from network layer
			if(self.event == "network_layer_ready"):
				packet = self.from_network_layer()
				self.buffer[self.next_frame_to_send] = packet
				self.nbuffered += 1
				self.send_data(self.next_frame_to_send,self.frame_expected)
				self.next_frame_to_send += 1

			#handling frame arrival at physical layer
			if(self.event == "frame_arrival"):
				frame = self.from_physical_layer()
				if(check_sum(frame) == False):
					continue;
				#handle data part
				if(frame.seq == self.frame_expected):
					packet = frame.info
					#send packet to network layer
					self.to_network_layer(packet)
					self.frame_expected += 1
				#handle ack part
				for i in range(ack_expected,r.ack + 1):
					self.nbuffered -= 1
					if(i == ack_expected):
						stop_timer()
					self.ack_expected += 1

			#handling time_out
			if(self.event == "timeout"):
				#start repeating from the frame whose ack was not received
				self.next_frame_to_send = self.ack_expected
				for i in range(nbuffered):
					self.send_data(self.next_frame_to_send,self.frame_expected)
					self.next_frame_to_send += 1

			if(self.nbuffered < self.MAX_SEQ):
				self.enable_network_layer()
			else:
				self.disable_network_layer()






