import time
import socket
import random
import thread
import sys
from random import randint
from threading import Lock, Thread

lock = Lock()

BIG_NUMBER = 1000000000000

# this is set by data layer
NETWORK_LAYER_ENABLED = False
# this is set by network layer
NETWORK_LAYER_READY = False

MAX_PACKET_LENGTH = 240

PACKET_SEQUENCE = 0

HOST_ID = sys.argv[1]

TOTAL_HEADER_LENGTH = 32

UDP_IP = sys.argv[3]
UDP_PORT = 7777

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((sys.argv[2], UDP_PORT))
# sleep to allow sockets to set up
time.sleep(2)

VERBOSE_MODE=False
if (len(sys.argv)>4):
    VERBOSE_MODE=True

PAYLOAD_BYTES_SENT=0
PAYLOAD_BYTES_RECEIVED=0
PACKETS_RECEIVED=0

class Packet:
    def __init__(self):
        self.seq = PACKET_SEQUENCE
        self.host = HOST_ID
        payload_string = "datadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadatadata"
        payload_length = random.randint(0, MAX_PACKET_LENGTH)
        self.info = payload_string[:payload_length]


class NetworkLayer:
    def __init__(self):
        if VERBOSE_MODE:
            f = open("received_packets"+str(HOST_ID)+".txt", "w")
            f.write("Network layer on host "+str(HOST_ID)+" initialised\n")
            f.close()
            f = open("sent_packets"+str(HOST_ID)+".txt", "w")
            f.write("Network layer on host "+str(HOST_ID)+" initialised\n")
            f.close()

    def send_packet(self):
        a = Packet()
        global PACKET_SEQUENCE
        global PAYLOAD_BYTES_SENT
        PACKET_SEQUENCE += 1
        PAYLOAD_BYTES_SENT += len(a.info)
        if VERBOSE_MODE:
            f = open("sent_packets"+str(HOST_ID)+".txt", "a+")
            f.write("{:12.2f}".format(time.time()) + ": Sent packet " +
                    str(a.seq) + " of size " + str(len(a.info)) + "\n")
            f.close()
        return a

    def receive_packet(self, packet):
        global PAYLOAD_BYTES_RECEIVED
        global PACKETS_RECEIVED
        PACKETS_RECEIVED+=1
        PAYLOAD_BYTES_RECEIVED+=len(packet.info)
        if VERBOSE_MODE:
            f = open("received_packets"+str(HOST_ID)+".txt", "a+")
            f.write("{:12.2f}".format(time.time()) + ": Received " + str(packet.seq) +
                    " from " + str(packet.host) + " of length " + str(len(packet.info)))
            f.write("\n")
            f.close()


# global network layer
network_layer = NetworkLayer()


class Frame:
    def __init__(self, seq_nr, ack_nr, info):
        self.seq = seq_nr
        self.ack = ack_nr
        # info is of type Packet
        self.info = info
        self.checksum = ""


class DataLinkLayer:
    def __init__(self, MAX_SEQ, TIME_FOR_ACK):
        # Initializations
        self.next_frame_to_send = 0
        self.ack_expected = 0
        self.frame_expected = 0
        # buffer contains packets, a maximum of MAX_SEQ
        self.buffer = [Packet()]*(MAX_SEQ + 1)  # why packet here!
        self.nbuffered = 0
        self.event = None
        self.network_layer_enabled = False
        self.MAX_SEQ = MAX_SEQ
        # timer times the last expected ack
        self.timer = time.time()
        self.TIME_FOR_ACK = TIME_FOR_ACK
        self.frame_available = False
        self.data_list = []
        self.timers = {}
        for i in range(MAX_SEQ + 1):
            self.timers[i] = BIG_NUMBER

    def enable_network_layer(self):
        global NETWORK_LAYER_ENABLED
        NETWORK_LAYER_ENABLED = True

    def disable_network_layer(self):
        global NETWORK_LAYER_ENABLED
        NETWORK_LAYER_ENABLED = False

    def start_timer(self, frame_nr):
        self.timers[frame_nr] = time.time()

    def stop_timer(self, ack_expected):
        self.timers[ack_expected] = BIG_NUMBER

    def time_over(self):
        return (time.time() - self.timers[self.ack_expected]) > self.TIME_FOR_ACK

    def to_physical_layer(self, frame):
        packet = frame.info

        #stringifying packet
        packet_str = str(packet.seq) + "_" + \
            str(packet.host) + "_" + str(packet.info)

        #stringifying frame
        frame_str = str(frame.seq) + "_" + str(frame.ack)
        message = packet_str + "_" + frame_str
        check_sum_string = self.gen_check_sum(message)
        message += "_" + check_sum_string
        print str(time.time()), ": Sent frame", str(
            frame.seq), "with Ack", str(frame.ack)

        #sending via socket
        sock.sendto(message, (UDP_IP, UDP_PORT))

    def convertStrToFrame(self, string):
        l = string.split("_")
        p = Packet()
        p.seq = int(l[0])
        p.host = int(l[1])
        p.info = l[2]
        seq = int(l[3])
        ack = int(l[4])
        info = p
        f = Frame(seq, ack, info)
        f.checksum = l[5]
        return f

    # returns false if frame has not arrived
    # if frame has arrived, set frame_available to true
    def from_physical_layer(self):
        data = self.data_list[0]
        self.data_list.remove(self.data_list[0])
        frame = self.convertStrToFrame(data)
        return frame

    def run_physical_layer(self):
        while(True):
            try:
                data = sock.recv(4096)
                if(len(data) != 0):
                    self.frame_available = True
                    self.data_list.append(data)
                else:
                    self.frame_available = False
            except:
                continue

    def send_data(self, frame_nr, frame_expected):
        info = self.buffer[frame_nr]
        seq = frame_nr
        ack = (frame_expected + self.MAX_SEQ) % (self.MAX_SEQ + 1)
        s = Frame(seq, ack, info)
        packet = s.info
        frame_str = str(packet.seq) + "_" + str(packet.host) + \
            "_" + str(packet.info) + str(s.seq) + "_" + str(s.ack)
        checksum = self.gen_check_sum(frame_str)
        s.checksum = checksum
        self.to_physical_layer(s)
        self.start_timer(frame_nr)

    def to_network_layer(self, packet):
        network_layer.receive_packet(packet)

    def from_network_layer(self):
        if(NETWORK_LAYER_ENABLED):
            packet = network_layer.send_packet()
            return packet

    def run_network_layer(self):
        while(True):
            global NETWORK_LAYER_READY
            if (int(time.time()*1000) % 2 == 1):
                NETWORK_LAYER_READY = True
            else:
                NETWORK_LAYER_READY = False

    def gen_check_sum(self, frame_string):
        return str(hash(frame_string) % 1024)

    def check_sum(self, frame):
        frame_string = str(frame.info.seq)+"_"+str(frame.info.host)+"_" + \
            str(frame.info.info)+"_"+str(frame.seq) + "_" + str(frame.ack)
        if (self.gen_check_sum(frame_string) == frame.checksum):
            return True
        else:
            return False

    def between(self, a, b, c):
        return (a <= b and b < c) or (b <= c and c < a) or (c <= a and a < b)

    def GBN_protocol(self):
        self.enable_network_layer()
        thread.start_new_thread(self.run_network_layer, ())
        thread.start_new_thread(self.run_physical_layer, ())

        frames_sent = 0
        frames_resent = 0
        frames_arrived_correct = 0
        frames_arrived_csum = 0
        time_begin = time.time()
        
        while(time.time()-time_begin < 30):
            global NETWORK_LAYER_READY

            # set event here
            if(NETWORK_LAYER_READY and NETWORK_LAYER_ENABLED):
                self.event = "network_layer_ready"
            elif(len(self.data_list) > 0):
                self.event = "frame_arrival"
            elif(self.time_over()):
                self.event = "timeout"
            else:
                self.event = "Nothing happening right now"

            if (self.event != "Nothing happening right now"):
                print ""
                print "Event: " + self.event

            # handling packets from network layer
            if(self.event == "network_layer_ready"):
                packet = self.from_network_layer()

                if(packet != None):
                    self.buffer[self.next_frame_to_send] = packet
                    self.nbuffered += 1
                    frames_sent += 1
                    self.send_data(self.next_frame_to_send,
                                   self.frame_expected)
                    self.next_frame_to_send = (
                        self.next_frame_to_send + 1) % (self.MAX_SEQ + 1)

            # handling frame arrival at physical layer
            if(self.event == "frame_arrival"):
                self.frame_available = False
                frame = self.from_physical_layer()
                if(self.check_sum(frame) == False):
                    print "Checksum Error"
                    frames_arrived_csum += 1
                    continue
                # handle data part
                print "Frame Expected:", self.frame_expected, "Frame received:", frame.seq
                if(frame.seq == self.frame_expected):
                    frames_arrived_correct += 1
                    packet = frame.info
                    # send packet to network layer
                    self.to_network_layer(packet)
                    self.frame_expected = (
                        self.frame_expected + 1) % (self.MAX_SEQ + 1)
                # handle ack part
                    print "Ack expected:", self.ack_expected, "Ack received:", frame.ack
                    while(self.between(self.ack_expected, frame.ack, self.next_frame_to_send)):
                        self.nbuffered -= 1
                        self.stop_timer(self.ack_expected)
                        self.ack_expected = (
                            self.ack_expected + 1) % (self.MAX_SEQ + 1)

            # handling time_out
            if(self.event == "timeout"):
                # start repeating from the frame whose ack was not received
                print "Timeout"
                self.next_frame_to_send = self.ack_expected
                for i in range(self.nbuffered):
                    frames_resent += 1
                    self.send_data(self.next_frame_to_send,
                                   self.frame_expected)
                    self.next_frame_to_send = (
                        self.next_frame_to_send + 1) % (self.MAX_SEQ + 1)

            if(self.nbuffered < self.MAX_SEQ):
                self.enable_network_layer()
            else:
                self.disable_network_layer()

        print "\n Host",str(HOST_ID),"TRANSMISSION SUMMARY"
        print "Total Frames transmitted: ",frames_sent + frames_resent
        print "Frames retransmitted: ",frames_resent
        print "Packets sent: ",PACKET_SEQUENCE
        print "Payload bytes sent: ", PAYLOAD_BYTES_SENT
        print "\n Host",str(HOST_ID),"RECEPTION SUMMARY"
        print "Frames received with checksum error: ",frames_arrived_csum 
        print "Frames received with no error: ", frames_arrived_correct
        print "Packets received: ",PACKETS_RECEIVED
        print "Payload bytes received: ", PAYLOAD_BYTES_RECEIVED



d = DataLinkLayer(7, 1)

d.GBN_protocol()
