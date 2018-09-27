#The following things need to be multi-threaded
# 2. from_physical_layer function of data layer
# 3. from_network_layer function of data layer

import time
import socket
import random
import thread
import sys
from random import randint
from threading import Lock, Thread

lock = Lock()

#this is set by data layer
NETWORK_LAYER_ENABLED = False
#this is set by network layer
NETWORK_LAYER_READY = False

MAX_PACKET_LENGTH = 240

PACKET_SEQUENCE = 0

HOST_ID = sys.argv[1]

TOTAL_HEADER_LENGTH = 32

UDP_IP = sys.argv[2]
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((sys.argv[3],5005))

class Packet:
	def __init__(self):
		global PACKET_SEQUENCE
		self.seq = PACKET_SEQUENCE
		self.host = HOST_ID
		PACKET_SEQUENCE+=1
		payload_string = "datadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadata"
		payload_length = random.randint(0,MAX_PACKET_LENGTH)
		self.info = payload_string[:payload_length]

class NetworkLayer:
	def __init__(self):
		f = open("packet_dump"+str(HOST_ID)+".txt","w")
		f.write("Network layer on host "+str(HOST_ID)+" initialised\n")
		f.close()

	def send_packet(self):
		a = Packet()
		print "sent packet " + str(a.seq) + " of size " + str(len(a.info))
		return a

	def receive_packet(self, packet):
		# print "hi here"
		f = open("packet_dump"+str(HOST_ID)+".txt","a+")
		f.write(str(time.time()) + " " + str(packet.seq) + " " + str(packet.host) + " " + str(len(packet.info)) + " " + packet.info)
		f.write("\n")
		f.close()

#global network layer
network_layer = NetworkLayer()

class Frame:
	def __init__(self,seq_nr,ack_nr,info):
		self.seq = seq_nr
		self.ack = ack_nr
		#info is of type Packet
		self.info = info
		self.checksum = ""

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
		self.timer = time.time()
		self.TIME_FOR_ACK = TIME_FOR_ACK
		self.frame_available = False
		self.data_list = []

	def enable_network_layer(self):
		global NETWORK_LAYER_ENABLED
		NETWORK_LAYER_ENABLED = True

	def disable_network_layer(self):
		global NETWORK_LAYER_ENABLED
		NETWORK_LAYER_ENABLED = False

	def start_timer(self):
		self.timer = time.time()

	def stop_timer(self):
		self.timer = 0

	def time_over(self):
		print time.time() - self.timer, self.TIME_FOR_ACK
		return (time.time() - self.timer) > self.TIME_FOR_ACK

	def to_physical_layer(self,frame):
		packet = frame.info
		packet_str = str(packet.seq) + "_" + str(packet.host) + "_" + str(packet.info)
		frame_str = str(frame.seq) + "_" +  str(frame.ack)
		message = packet_str + "_" + frame_str 
		check_sum_string = self.gen_check_sum(message)
		message += "_" + check_sum_string
		sock.sendto(message,(UDP_IP,UDP_PORT))
	
	def convertStrToFrame(self,string):
		l = string.split("_")
		p = Packet()
		p.seq = int(l[0])
		p.host = int(l[1])
		p.info = l[2]
		seq = int(l[3])
		ack = int(l[4])
		info = p
		f = Frame(seq,ack,info)
		f.checksum = l[5]
		return f

	#returns false if frame has not arrived
	#if frame has arrived, set frame_available to true
	def from_physical_layer(self):
			data = self.data_list[-1]
			frame = self.convertStrToFrame(data)
			return frame

	def run_physical_layer(self):
		while(True):
			try:
				data = sock.recv(4096)
				# print len(data), "ferer"
				if(len(data) != 0):
					self.frame_available = True
					self.data_list.append(data)
				else:
					self.frame_available = False
			except:
				continue

	def send_data(self,frame_nr,frame_expected):
		info = self.buffer[frame_nr]
		#print frame_nr,info
		seq = frame_nr
		ack = (frame_expected + self.MAX_SEQ)%(self.MAX_SEQ + 1)
		s = Frame(seq,ack,info)
		packet = s.info
		frame_str = str(packet.seq) + "_" + str(packet.host) + "_" + str(packet.info) + str(s.seq) + "_" +  str(s.ack)
		checksum = self.gen_check_sum(frame_str)
		s.checksum = checksum
		self.to_physical_layer(s)
		self.start_timer()

	def to_network_layer(self,packet):
		# print "hi again"
		network_layer.receive_packet(packet)

	def from_network_layer(self):
		if(NETWORK_LAYER_ENABLED):
			packet = network_layer.send_packet()
			return packet

	def run_network_layer(self):
		while(True):
			global NETWORK_LAYER_READY
			if (int(time.time()*1)%2 == 1):
				NETWORK_LAYER_READY = True
			else:
				NETWORK_LAYER_READY = False


	def gen_check_sum(self,frame_string):
		return str(hash(frame_string)%1024)

	def check_sum(self,frame):
		frame_string = str(frame.info.seq)+"_"+str(frame.info.host)+"_"+str(frame.info.info)+"_"+str(frame.seq) + "_" + str(frame.ack)
		if (self.gen_check_sum(frame_string)==frame.checksum):
			return True
		else:
			return False

	def between(self,a,b,c):
		return (a <= b and b < c) or (b <= c and c < a) or (c <= a and a < b)

	def GBN_protocol(self):
		self.enable_network_layer();
		thread.start_new_thread(self.run_network_layer,())
		thread.start_new_thread(self.run_physical_layer,())
		while(True):
			global NETWORK_LAYER_READY
			# print NETWORK_LAYER_READY, NETWORK_LAYER_ENABLED, self.frame_available, self.time_over()
			# print self.nbuffered, "rbrzbre"
			#set event here
			# print self.event
			if(NETWORK_LAYER_READY and NETWORK_LAYER_ENABLED):
				self.event = "network_layer_ready"
			elif(self.frame_available):
				self.event = "frame_arrival"
			elif(self.time_over()):
				self.event = "timeout"
			else:
				self.event = "Nothing happening right now"
			#handling packets from network layer
			if(self.event == "network_layer_ready"):
				print "network_layer_ready"
				packet = self.from_network_layer()

				#print self.next_frame_to_send, self.buffer
				if(packet != None):
					self.buffer[self.next_frame_to_send] = packet
					self.nbuffered += 1
					
					self.send_data(self.next_frame_to_send,self.frame_expected)
					self.next_frame_to_send  = (self.next_frame_to_send + 1)%(self.MAX_SEQ + 1)

			#handling frame arrival at physical layer
			if(self.event == "frame_arrival"):
				self.frame_available=False
				frame = self.from_physical_layer()
				if(self.check_sum(frame) == False):
					continue;
				#handle data part
				if(frame.seq == self.frame_expected):
					print "frame arrival"

					packet = frame.info
					#send packet to network layer
					self.to_network_layer(packet)
					self.frame_expected = (self.frame_expected + 1)%(self.MAX_SEQ + 1)
				#handle ack part
				print self.ack_expected, frame.ack + 1, "vdsrsf"
				while(self.between(self.ack_expected,frame.ack,self.next_frame_to_send)):
					self.nbuffered -= 1
					if(frame.ack == self.ack_expected):
						self.stop_timer()
					self.ack_expected = (self.ack_expected + 1)%(self.MAX_SEQ + 1)

			#handling time_out
			if(self.event == "timeout"):
				#start repeating from the frame whose ack was not received
				print "timeout"
				self.next_frame_to_send = self.ack_expected
				for i in range(self.nbuffered):
					self.send_data(self.next_frame_to_send,self.frame_expected)
					self.next_frame_to_send = (self.next_frame_to_send + 1)%(self.MAX_SEQ + 1)

			if(self.nbuffered < self.MAX_SEQ):
				self.enable_network_layer()
			else:
				self.disable_network_layer()


d = DataLinkLayer(20,1)

d.GBN_protocol()



