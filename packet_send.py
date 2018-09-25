#!/usr/bin/python
from scapy.all import *
from random import randint

MAX_PACKET_LENGTH = 40

class Network_Layer(Packet):
	name = 'network_layer'
	fields_desc = [
		BitField('hostID', 0, 1),
		ShortField('seqNumber', 0),
	]

def get_network_layer():
	a = Network_Layer(hostID=1,seqNumber=256)
	payload_string = "datadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadata"
	payload_length = randint()%MAX_PACKET_LENGTH
	return a/payload_string[:payload_length]

def send_packet(frame):
	data_frame = Ether()/IP(src="",dst="")/frame
	ack_frame = Ether()/IP(src="",dst="")/Data_Link_Layer()


Data_Link_Layer()/frame