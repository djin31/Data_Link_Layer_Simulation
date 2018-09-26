import time
from random import randint
from threading import Lock, Thread

lock = Lock()
#this is set by data layer
NETWORK_LAYER_ENABLED = False
#this is set by network layer
NETWORK_LAYER_READY = False

PACKET_SEQUENCE = 0

HOST_ID = 0

TOTAL_HEADER_LENGTH = 32

COMPLEMENT_HOST_IP = "127.0.0.1"
PORT_NO = 7777

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
			s = str(a.seq) + "/" + str(a.host) + "/" + a.info
			return s

	def receive_packet(self, string_packet):
		f=open("packet_dump"+str(HOST_ID)+".txt","a+")
		f.write("%f\t%d\n" %(str(time.time(),len(string_packet))))
		f.close()

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
		pass
	#returns false if frame has not arrived
	#if frame has arrived, set frame_available to true
	def from_physical_layer():
		pass

	def send_data(frame_nr,frame_expected):
		pass

	def to_network_layer(packet):
		pass

	def from_network_layer():
		pass

	def check_sum(frame):
		pass

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
					stop_timer(i)
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






