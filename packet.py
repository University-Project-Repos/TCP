"""
COSC264 Networking assignment
The packet program for the TCP socket assignment.
Author:
    - Adam Ross
"""

from struct import pack, unpack


class Packet:

    MAGIC_NO = 0x497E  # The unique hexadecimal value to identify valid packets
    PTYPE_DATA = 0  # The value representing data packets
    PTYPE_ACK = 1  # The value representing acknowledgement packets
    MAX_BYTES = 512  # Maximum chars read from a file
    HEADER = 20  # The sum of the bytes of 4 packed integer values
    FORMAT_STR = "iiiii"

    def __init__(self, magic_no, data_type, seq_no, data_len, data):
        self.magic_no = magic_no  # For identifying a packets validity
        self.data_type = data_type  # Distinguishes the packet type
        self.seq_no = seq_no  # Distinguishes a packets position in a sequence
        self.data_len = data_len  # Declares the length of the data in the packet
        self.data = data  # Contains data at a length specified in dataLen

    def is_magic(self):
        """
        Checks if magic_no value in a packet is equal to MAGIC_NO value
        :return: True if magic_no is equal to MAGIC_NO value, otherwise False
        """
        return self.magic_no == self.MAGIC_NO

    def sender_check(self):
        """
        Checks if data received is not an acknowledgement packet
        :return: True if packet is not an acknowledgement packet, otherwise False
        """
        data_type, data_len = self.data_type, self.data_len
        return not Packet.is_magic(self) or data_type != self.PTYPE_ACK or data_len != 0

    def receiver_check(self):
        """
        Checks if data received is a valid data packet
        :return: True if packet is a valid data packet, otherwise False
        """
        return Packet.is_magic(self) and self.data_type == self.PTYPE_DATA

    def buffer(self, chk_sum):
        """
        Turns a package of data into a byte pack for TCP transmitting
        :param chk_sum: checksum of the packet
        :return: byte pack
        """
        fmt = self.FORMAT_STR + str(self.data_len) + 's'
        data_type, seq_no, data_len = self.data_type, self.seq_no, self.data_len
        return pack(fmt, chk_sum, self.magic_no, data_type, seq_no, data_len, self.data)

    @staticmethod
    def un_buffer(byte_packet):
        """
        Unpacks received byte pack and converts it to a data packet
        :param byte_packet: byte packet received from TCP socket
        :return: data packet, check sum of the packet
        """
        hdr = unpack(Packet.FORMAT_STR, byte_packet[:Packet.HEADER])  # Unpacks 4 header integers
        chk_sum, magic_no, data_type, seq_no, data_len = hdr[0], hdr[1], hdr[2], hdr[3], hdr[4]

        if chk_sum != (magic_no + data_type + seq_no + data_len):
            data_len = chk_sum - (magic_no + data_type + seq_no)  # Fixes data len from bit err
        data = unpack(str(data_len) + 's', byte_packet[Packet.HEADER:data_len + Packet.HEADER])
        return Packet(magic_no, data_type, seq_no, data_len, data[0]), chk_sum
