# get_length_word(packet_length, ack_num, seq_num) -- gets the 16 bit number with ack and seq num embedded in it
# sum_words_in_packet(packet) -- groups the function into 16 bits and calculates the sum
# extract_message_from_packet(packet) -- extracts the message from the given packet
# extract_sequence_num_from_packet(packet) -- This method returns a single bit that represents the sequence number in the given packet
# extract_ack_from_packet(packet) -- This method returns a single bit that represents the ack number in the given packet


def create_checksum(packet_wo_checksum):
    """create the checksum of the packet (MUST-HAVE DO-NOT-CHANGE)

    Args:
      packet_wo_checksum: the packet byte data (including headers except for checksum field)

    Returns:
      the checksum in bytes

    """
    k = 16
    sum = sum_words_in_packet(packet_wo_checksum)

    if(len(sum) > k):
        x = len(sum)-k
        sum = bin(int(sum[0:x], 2)+int(sum[x:], 2))[2:]
    
    if(len(sum) < k):
        sum = '0'*(k-len(sum))+sum
    
    Checksum = ''
    for i in sum:
        if(i == '1'):
            Checksum += '0'
        else:
            Checksum += '1'
    
    return int(Checksum,2).to_bytes(2,'big')

def verify_checksum(packet):
    """verify packet checksum (MUST-HAVE DO-NOT-CHANGE)

    Args:
      packet: the whole (including original checksum) packet byte data

    Returns:
      True if the packet checksum is the same as specified in the checksum field
      False otherwise

    """    
    sum = create_checksum(packet)
    return 0 == int.from_bytes(sum, "big")

def make_packet(data_str, ack_num, seq_num):
    """Make a packet (MUST-HAVE DO-NOT-CHANGE)

    Args:
      data_str: the string of the data (to be put in the Data area)
      ack: an int tells if this packet is an ACK packet (1: ack, 0: non ack)
      seq_num: an int tells the sequence number, i.e., 0 or 1

    Returns:
      a created packet in bytes

    """
    initial_checksum = 0
    packet = list()
    packet.append(b'COMP')
    packet.append(b'NETW')
    packet.append(initial_checksum.to_bytes(2, 'big')) #place holder for checksum
    packet_length = 12 + len(data_str)
    packet.append(get_length_word(packet_length, ack_num, seq_num))
    packet.append(data_str.encode())
    packet_wo_checksum = b''.join(packet)
    checksum = create_checksum(packet_wo_checksum)
    packet[2] = checksum
    packet_with_checksum = b''.join(packet)
    return packet_with_checksum

def get_length_word(packet_length, ack_num, seq_num):
    """
    Returns 2 bytes representing length of the data with seq and ack added
    """
    packet_length = packet_length << 1
    packet_length = packet_length | ack_num
    packet_length = packet_length << 1
    packet_length = packet_length | seq_num
    return packet_length.to_bytes(2, 'big')

def sum_words_in_packet(packet):
  """
  Given a packet in Bytes, groups the bytes into words (2 bytes) and adds them to calculate the total sum of the packet

  Args
    Packet in bytes

  Returns
    A binary string representation of the sum of bits in the packet grouped into 16 bit word
  """
  packet_array = list(packet)
  sum = 0
  for i in range(0,len(packet_array),2):
    w1 = packet_array[i] & 0xFF
    w1 = w1 << 8
    w2 = 0
    if i + 1 < len(packet_array):
      w2 = packet_array[i+1] & 0xFF
      sum += w1 + w2
    
  ## substringing because bin() returns string with 0b prefixed
  sum = bin(sum)[2:]
  return sum

def extract_message_from_packet(packet):
  """
    This method returns the message portion of the given packet
    This method assumes the first 12 bytes are header + checksum and the message part starts only from the 13th byte

    Args
      packet in Bytes
  """
  packet_array = list(packet)
  return "".join(map(chr, packet_array[12:]))

def extract_sequence_num_from_packet(packet):
  """
    This method returns a single bit that represents the sequence number in the given packet
    This method assumes the sequence number is always the LSB of 12th byte of the packet
  """
  packet_array = list(packet)
  byte_with_sequence = packet_array[11]
  return byte_with_sequence & 0x01

def extract_ack_from_packet(packet):
  """
    This method returns a single bit that represents the ack number in the given packet
    This method assumes the ack number is always in the 12th byte of the packet

    Currently not in use
  """
  packet_array = list(packet)
  byte_with_sequence = packet_array[11]
  lsbs = byte_with_sequence & 0x02
  return lsbs >> 1




# make sure your packet follows the required format!


###### These three functions will be automatically tested while grading. ######
###### Hence, your implementation should not make any changes to         ######
###### the above function names and args list.                           ######
###### You can have other helper functions if needed.                    ######  
