##calculate_seq_to_send(packet_num, seq_num_received, msg) - This method returns the sequence number to send back to the client based on the packet number and simulates packet corruption and socket timeout

from socket import *
from time import sleep
from util import *

receiver_port = 10100+(4165219)%200
receiver_socket = socket(AF_INET, SOCK_STREAM)

# Binding proxy server socket
receiver_socket.bind(('', receiver_port))
receiver_socket.listen(15)
packet_num = 1
ack_num = 1
print("Server listening")

def calculate_seq_to_send(packet_num, seq_num_received, msg):
    """
    This method returns the sequence number to send back to the client based on the packet number
    This method simulates packet corruption and socket timeout
    """
    if packet_num % 6 == 0:
        print("simulating packet loss: sleep a while to trigger timeout event on the send side...")
        sleep(10)
        return None
    elif packet_num % 3 == 0:
        print("simulating packet bit errors/corrupted: ACK the previous packet")
        return 1 if seq_num_received == 0 else 0
    else:
        print("packet is expected, message string delivered: {0}".format(msg))
        print("packet is delivered, now creating and sending the ACK packet...")
        return seq_num_received

while True:
    sender_socket, sender_addr = receiver_socket.accept()
    client_packet = sender_socket.recv(1024)
    print("packet num.{0} received: {1}".format(packet_num, client_packet))   
    isPacketUntampered = verify_checksum(client_packet)
    msg = extract_message_from_packet(client_packet)
    seq_num_received = extract_sequence_num_from_packet(client_packet)
    seq_num_toSend = calculate_seq_to_send(packet_num, seq_num_received, msg)
    if seq_num_toSend != None:
        packet_to_send = make_packet(msg, ack_num, seq_num_toSend)
        sender_socket.send(packet_to_send)
    print("all done for this packet!\n\n")
    packet_num += 1
