class Packet:
	pass

class NetworkLayer:
	pass

class Frame:
	def __init__(self,frame_kind,seq_nr,ack_nr,info):
		self.seq = seq_nr
		self.ack = ack_nr
		#info is of type Packet
		self.info = info

class DataLinkLayer:
	def __init__(self, MAX_SEQ):
		#Initializations
		self.next_frame_to_send = 0
		self.ack_expected = 0
		self.frame_expected = 0
		#buffer contains packets
		self.buffer = []
		self.nbuffered = 0
		self.event = None
		self.network_layer_enabled = False
		self.MAX_SEQ = MAX_SEQ


	def enable_network_layer():
		self.network_layer_enabled = True

	def disable_network_layer():
		self.network_layer_enabled = False

	def start_timer(frame_nr):
		pass

	def stop_timer(ack_nr):
		pass

	def to_physical_layer(frame):
		pass

	def from_physical_layer(frame):
		pass

	def send_data(frame_nr,frame_expected):
		pass

	def to_network_layer(packet):
		pass

	def from_network_layer(packet):
		pass

	def GBN_protocol():
		pass
