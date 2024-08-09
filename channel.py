"""
COSC264 Networking assignment
The channel program for the TCP socket assignment
Author:
    - Adam Ross
"""

from random import uniform, randint
from tcp_transmission import TCP
from packet import Packet
from select import select
from time import time
from sys import argv


class Channel(TCP):

    CHANNEL = 'channel'  # name of the channel program file

    SENDER = 1
    RECEIVER = 0

    def __init__(self):
        super().__init__()
        self.program = self.CHANNEL

        self.packet_info = {
            self.SENDER: ["sender", "receiver", "Data"],
            self.RECEIVER: ["receiver", "sender", "Acknowledgement"]
        }

    def is_err(self, received_packet, p, loss_cnt, bit_cnt, transmission_cnt):
        """
        Check for correct magic_no, packet loss, and bit errors
        """
        u, v, max_incr = round(uniform(0, 1), 4), round(uniform(0, 1), 4), 10

        #  check if the packet is not valid and drops if so
        if not received_packet or not received_packet.is_magic():
            transmission_cnt += 1  # increment transmission count
            print("Received packet invalid. Packet dropped.")
            return received_packet, loss_cnt, bit_cnt, transmission_cnt + 1, True

        #  check if μ value is less than the probability of a packet loss event
        if u < p:
            loss_cnt += 1  # packet loss count incremented
            print("A μ value of " + str(u) + " < " + str(p) + ", indicating #" +
                  str(loss_cnt) +
                  " occurrence of the probability of a packet loss event")
            return received_packet, loss_cnt, bit_cnt, transmission_cnt + 1, True

        # check if v value is less than the probability of a bit error event
        if v < self.BIT_ERR:
            bit_cnt += 1  # bit error count incremented
            print("A v value of " + str(v) + " < " + str(self.BIT_ERR) +
                  ", indicating #" + str(bit_cnt) +
                  " occurrence of the probability of a bit error event")
            received_packet.data_len += randint(1, max_incr)  # increment data_len
        return received_packet, loss_cnt, bit_cnt, transmission_cnt, False

    def check_p_in_range(self, p):
        """
        Check if the P value is a float within the range of 0.0 and 1.0.
        If not, print a message and prompt for a new P value input
        """
        while not float(p) >= 0.0 or not float(p) < 1.0:
            print("\nError! 'P' value " + str(p) + " is not a float value >= " + str(0.0) + " and < " + str(1.0) + ".")
            p = input("Re-enter a valid 'P' float value: ")
            p = self.check_instance(p, float)

    def print_packet_transmission_success(self, packet_data_transmitter, received_packet, is_sending=True):
        print(self.packet_info[packet_data_transmitter][2] + " packet containing " + str(received_packet.data_len) +
              " chars transmitted" + (" to " if is_sending else " from ") +
              self.packet_info[packet_data_transmitter][int(is_sending)])

    def run(self, cs_in, cs_out, cr_in, cr_out, s_in, r_in, p):
        """
        Receive and send packets between programs using TCP connections
        """
        self.check_p_in_range(p)  # checks P float value is >= 0 and < 1

        trans, cont, end, err, packet_data_transmitter, timer = False, False, False, False, None, time()
        p_cnt, r_cnt, snt, lss, bit, error_countdown = 0, 0, 0, 0, 0, 10

        self.ports = {
            'csIn': cs_in,
            'csOut': cs_out,
            'crIn': cr_in,
            'crOut': cr_out,
            'sIn': s_in,
            'rIn': r_in
        }  # dictionary for ports
        self.socks = {
            'csIn': None,
            'csOut': None,
            'crIn': None,
            'crOut': None
        }  # dictionary for sockets

        self.port_socket_init()  # init ports, sockets
        r_conn = [self.socks['crIn'], self.socks['crOut'], self.ports['rIn']]  # receiver connection data
        s_conn = [self.socks['csIn'], self.socks['csOut'], self.ports['sIn']]  # sender connection data
        self.conns = [r_conn, s_conn]
        self.conn_init()  # init socket connections

        while True:
            is_readable, _, _ = select(self.conns, [], [], 1)  # wait for input on sockets
            received_packet = None

            if is_readable:  # if a packet of data is received from sender or receiver
                for read in is_readable:
                    try:
                        if read == self.conns[self.SENDER]:
                            # receive packet from sender program
                            received_packet, check_sum = Packet.un_buffer(self.conns[1].recv(self.BUFFER))
                            sock = self.socks['crOut']  # set socket for sending
                            packet_data_transmitter = self.SENDER

                            if len(received_packet.data) == 0:
                                end = True  # this indicates final data pack
                        elif read == self.conns[self.RECEIVER]:
                            # receive packet from the receiver program
                            received_packet, check_sum = Packet.un_buffer(self.conns[0].recv(self.BUFFER))
                            sock = self.socks['csOut']  # set socket for sending
                            packet_data_transmitter = self.RECEIVER

                        self.print_packet_transmission_success(packet_data_transmitter, received_packet, False)
                        trans, cont, err = True, True, False
                        r_cnt += 1  # increment the count of packets received
                    except Exception:
                        if not trans:  # if no packets have been received at all, timer resets as no conn is initiated
                            timer = time()
                            continue
                        elif error_countdown > 0:
                            error_countdown -= 1
                        else:
                            self.conn_error()  # closes program when connection is lost or deadlock event

                    # if transmitting, checks for packet loss, bit error, validity
                    if not (not cont and packet_data_transmitter == self.RECEIVER):
                        received_packet, lss, bit, snt, err = self.is_err(received_packet, p, lss, bit, snt)

                    # if there is neither packet loss, bit error, invalidity
                    if not err:
                        try:
                            sock.send(received_packet.buffer(check_sum))  # send packet

                            if cont:
                                self.print_packet_transmission_success(packet_data_transmitter, received_packet)
                                snt += 1  # increment total transmissions count

                                if packet_data_transmitter == self.RECEIVER:
                                    p_cnt += 2  # increment data packet count
                        except Exception:
                            if trans and not cont:
                                print("All TCP transmissions are complete")
                                counts = [snt, r_cnt, p, lss, bit, time() - timer]
                                self.trans_finn(counts, p_cnt)
                            if trans or error_countdown <= 0:  # when connection is lost or deadlock event
                                self.conn_error()  # closes program
                            else:
                                error_countdown -= 1

                    if end and packet_data_transmitter == self.RECEIVER:
                        cont = False  # set the continue variable to False if final packet


def main(arguments):
    tcp_app_channel = Channel()
    vals = tcp_app_channel.validate_args(arguments, 8, [int] * 6 + [float])
    tcp_app_channel.run(vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6])


if __name__ == '__main__':
    main(argv)
