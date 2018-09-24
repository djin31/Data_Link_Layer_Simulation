#!/usr/bin/python
from scapy.all import *

class Network_Layer(Packet):
	name = 'network_layer'
	fields_desc = [
		BitField('hostID', 0, 1),
		ShortField('seqNumber', 0),
	]



def send_packet():
	data_frame = Ether()/IP(src="",dst="")/Data_Link_Layer()/Network_Layer()
	ack_frame = Ether()/IP(src="",dst="")/Data_Link_Layer()


