"""
COSC264 Networking assignment
The receiver program for the TCP socket assignment.
Author:
    - Adam Ross
"""

from tcp_transmission import TCP
from packet import Packet
from select import select
from time import time
from sys import argv


class Receiver(TCP):

    RECEIVER = 'receiver'  # name of the receiver program file

    def __init__(self):
        super().__init__()
        self.program = self.RECEIVER

    def run(self, r_in, r_out, cr_in, file_name):
        """
        Transmit packets to/from the channel program using TCP connection
        """
        file = self.open_file(file_name)  # open a file for writing received data to

        expected, s_cnt, r_cnt, p_cnt, fails = 0, 0, 0, 1, 0

        self.ports = {
            'rIn': r_in,
            'rOut': r_out,
            'crIn': cr_in
        }  # dictionary for ports
        self.socks = {
            'rIn': None,
            'rOut': None
        }  # dictionary for the sockets

        self.port_socket_init()  # init ports, sockets
        self.conns = [[self.socks['rIn'], self.socks['rOut'], self.ports['crIn']]]  # connection data
        timer = self.conn_init()  # init socket connections

        while True:
            is_readable, _, _ = select(self.conns, [], [], 1)  # wait for input on socket

            if is_readable:  # if a packet of data is received from channel
                received_packet, fails, error = self.receive_packet(fails, 1, file)
                if error:
                    continue
                r_cnt += 1  # increment received packet count

                check_sum = Packet.MAGIC_NO + Packet.PTYPE_ACK + received_packet.seq_no  # packet validation

                if received_packet.receiver_check():  # send acknowledgement packet
                    if received_packet.seq_no != expected:  # resend last acknowledgement pack
                        out_pack = Packet(Packet.MAGIC_NO, Packet.PTYPE_ACK, received_packet.seq_no, 0, b'')

                        self.send_packet('rOut', out_pack, check_sum, file)
                        s_cnt += 1  # increment sent packet count
                    else:  # send new acknowledgement packet, write/print data
                        p_cnt = self.print_data(received_packet.data, p_cnt, len(received_packet.data))
                        out_pack = Packet(Packet.MAGIC_NO, Packet.PTYPE_ACK, received_packet.seq_no, 0, b'')

                        self.send_packet('rOut', out_pack, check_sum, file)
                        expected = 1 - expected  # toggle expected between 1 and 0
                        s_cnt += 1  # increment sent packet count

                        if received_packet.data_len > 0:
                            file.write(received_packet.data)  # write received data to file
                        else:
                            # terminate program, closes sockets and connections
                            self.trans_finn([s_cnt, r_cnt], p_cnt, file)
                else:
                    self.print_invalid_packet(list(self.programs.keys()).index(self.program) + 1)

            if (time() - timer) > self.TIME_OUT and r_cnt == 0:  # connection time-out
                self.conn_error(file)  # close program


def main(arguments):
    tcp_app_receiver = Receiver()
    vals = tcp_app_receiver.validate_args(arguments, 5, [int] * 3 + [str])
    print(vals)
    tcp_app_receiver.run(vals[0], vals[1], vals[2], vals[3])


if __name__ == '__main__':
    main(argv)
