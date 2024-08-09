"""
COSC264 Networking assignment
The sender program for the TCP socket assignment.
Authors:
    - Adam Ross
    - Helen Yang (and/or tutor(s))
"""

from tcp_transmission import TCP
from packet import Packet
from select import select
from time import time
from sys import argv


class Sender(TCP):

    SENDER = 'sender'  # name of the sender program file

    def __init__(self):
        super().__init__()
        self.program = self.SENDER

    def sender(self, s_in, s_out, cs_in, file_name):
        """
        Sends data to other programs by the implementation of TCP connections
        """
        file = self.open_file(file_name)  # opens the file for reading data from

        exit_flag, nxt, p_cnt, r_cnt, s_cnt, fails = False, 0, 1, 0, 0, 0

        self.ports = {
            'sIn': s_in,
            'sOut': s_out,
            'csIn': cs_in
        }  # dictionary for ports
        self.socks = {
            'sIn': None,
            'sOut': None
        }  # dictionary for sockets

        self.port_socket_init()  # init ports, sockets
        self.conns = [[self.socks['sIn'], self.socks['sOut'], self.ports['csIn']]]  # connection data
        timer = self.conn_init()  # init socket connections

        while not exit_flag:
            packet_count = 0  # initialize a count of data sending attempts to zero
            data = file.read(Packet.MAX_BYTES)  # read at most 512 characters from a file

            if len(data) == 0:  # create empty data packet to declare end of file
                data_pack = Packet(Packet.MAGIC_NO, Packet.PTYPE_DATA, nxt, 0, b'')
                exit_flag = True  # exit_flag is set to True to exit from while loop
            else:
                data_pack = Packet(Packet.MAGIC_NO, Packet.PTYPE_DATA, nxt, len(data), data)
            check_sum = Packet.MAGIC_NO + Packet.PTYPE_DATA + data_pack.seq_no + data_pack.data_len

            while True:
                self.send_packet('sOut', data_pack, check_sum, file)
                packet_count += 1  # increment packet sending attempts by 1
                readable, _, _ = select(self.conns, [], [], 1)  # wait for input on sock

                if readable:  # if a packet of data is received from channel
                    received_packet, fails, error = self.receive_packet(fails, -1, file)
                    if error:
                        continue
                    r_cnt += 1

                    if received_packet.sender_check():  # check if data is invalid
                        self.print_invalid_packet(list(self.programs.keys()).index(self.program) - 1)
                        continue

                    if received_packet.seq_no == nxt:  # check if seq_no is equal to send data
                        p_cnt = self.print_data(data, p_cnt, len(data), packet_count)
                        s_cnt += packet_count  # increment sent data count
                        nxt = 1 - nxt  # toggle next between a value of 0 and 1
                        break

                if ((time() - timer) > self.TIME_OUT and r_cnt == 0) or fails > self.TIME_OUT:
                    self.conn_error(file)  # close program
        self.trans_finn([s_cnt, r_cnt], p_cnt, file)  # close program


def main(arguments):
    tcp_app_sender = Sender()
    vals = tcp_app_sender.validate_args(arguments, 5, [int] * 3 + [str])
    tcp_app_sender.sender(vals[0], vals[1], vals[2], vals[3])


if __name__ == '__main__':
    main(argv)
