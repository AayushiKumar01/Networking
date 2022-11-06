# get_socket() -- creates a socket obbject
# get_print_message_based_on_packet_status(app_msg_str) -- gets the message to print based on packet status
# send_message(app_msg_str) -- sends the given message to the server


from socket import *
from util import *

class Sender:
  ack_num = 0
  seq_num = 0
  packet_num = 1
  packet_status = 1 #can have 3 status, 1 = original message, 2 = retranmission, 3 = socket timed out
  receiver_ip = '127.0.0.1'
  receiver_port = 10119


  def __init__(self):
    """ 
    Your constructor should not expect any argument passed in,
    as an object will be initialized as follows:
    sender = Sender()
     
    Please check the main.py for a reference of how your function will be called.
    """


  def rdt_send(self, app_msg_str):
    """realibly send a message to the receiver (MUST-HAVE DO-NOT-CHANGE)

    Args:
      app_msg_str: the message string (to be put in the data field of the packet)
      This method will keep transmiting the current message until it acknowledged by the server

    """
    ack_received = False
    original = True
    while ack_received == False:
      ack_received = self.send_message(app_msg_str)
      original = False
      self.packet_num += 1
      print("\n\n")
    self.seq_num = 1 if self.seq_num == 0 else 0


  def send_message(self, app_msg_str):
    """
    opens a socket connection and sends the given message to the server

    Args:
      app_msg_str: the message string (to be put in the data field of the packet)
    """
    sender_socket = self.get_socket()
    self.get_print_message_based_on_packet_status(app_msg_str)
    packet_to_send = make_packet(app_msg_str, self.ack_num, self.seq_num)
    print("packet created: {0}".format(packet_to_send))
    
    ack_received = False
    try:
      sender_socket.send(packet_to_send)
      print("packet num.{0} is successfully sent to the receiver".format(self.packet_num))
      
      received_packet = sender_socket.recv(1024)
      received_seq = extract_sequence_num_from_packet(received_packet)
      
      ack_received = received_seq == self.seq_num
      if ack_received:
        print("packet is received correctly: seq. num = {0} ACK num {1}. all done!".format(self.seq_num, self.seq_num))
        self.packet_status = 1
      else:
        print("receiver acked the previous pkt, resend!")
        self.packet_status = 2

    except Exception as e:
      print("socket timeout! Resend!")
      self.packet_status = 3
    
    sender_socket.close()
    return ack_received
 
  
  def get_print_message_based_on_packet_status(self, app_msg_str):
    """
    Prints the initial message based on the status of the cuurent packet
    """
    if self.packet_status == 1:
      print("original message string: {0}".format(app_msg_str))
    elif self.packet_status == 2:
      print("[ACK-Previous retransmission]: {0}".format(app_msg_str))
    else:
      print("[timeout retransmission]: {0}".format(app_msg_str))
  
  
  def get_socket(self):
    """
    Initializes the socket
    """
    sender_socket = socket(AF_INET, SOCK_STREAM)
    sender_socket.connect((self.receiver_ip, self.receiver_port))
    sender_socket.settimeout(10)
    return sender_socket

  
  
  ####### Your Sender class in sender.py MUST have the rdt_send(app_msg_str)  #######
  ####### function, which will be called by an application to                 #######
  ####### send a message. DO NOT Change the function name.                    #######                    
  ####### You can have other functions as needed.                             #######   