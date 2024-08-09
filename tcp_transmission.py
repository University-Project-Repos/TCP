"""
COSC264 Networking assignment
Main file for the TCP socket project app
Author:
    - Adam Ross
"""

from socket import socket, AF_INET, SOCK_STREAM, error as socket_error
from struct import error as struct_error
from os import path, system as terminal
from collections import Counter
from random import sample as rs
from select import select
from packet import Packet
from pathlib import Path
from time import time
from sys import argv


class TCP:

    LOOPBACK = '127.0.0.1'  # IP address used for TCP simulation
    BIT_ERR = 0.1  # probability of a bit error occurring
    MIN_RANGE = 1024  # minimum integer value for a port
    MAX_RANGE = 64000  # maximum integer value for a port
    BUFFER = Packet.MAX_BYTES + Packet.HEADER  # maximum number of bytes per recv
    TIME_OUT = 30  # max time/clocks before connections are deemed disrupted
    PACKET_DATA_DIVISOR = 5  # for iterating through packet data

    def __init__(self):
        self.socks = dict()  # dictionary for sockets
        self.ports = dict()  # dictionary for ports
        self.conns = list()  # list for socket connections

        self.programs = {
            'channel': '<csIn> <csOut> <crIn> <crOut> <sIn> <rIn> <P>',
            'receiver': '<rIn> <rOut> <crIn> <output file>',
            'sender': '<sIn> <sOut> <csIn> <input file>'
        }  # For error messages
        self.program = None
        self.programs_conn_counter = 0  # counter to know which program is being connected to

    def open_file(self, file_name):
        """
        Queries user to enter a file name if specified name doesn't exist
        """
        while not path.exists(file_name):
            if self.program == list(self.programs.keys())[2]:
                print("Error! File " + str(file_name) + " does not exist.")
                file_name = input("Re-enter a valid file name, or enter 'E' to abort: ")

                if file_name.upper() == 'E':
                    self.exit_program()  # Closes the program with an error message
            else:
                file_path = Path(file_name)
                file_path.touch()
        return open(file_name, 'rb' if self.program == list(self.programs.keys())[2] else 'wb')

    def exit_program(self):
        """
        Prints a declaration of correct input for running program and exits
        """
        print("\n" + str(self.program).capitalize() + " program aborted!\n" + str(self.program) +
              ".py requires: " + self.programs[self.program] + ".\n")
        exit()  # Exits the program

    def close_sockets_connections(self):
        """
        Closes all sockets and connections at termination of program
        """
        count = 0
        for connection in self.conns:  # iterates through all connections
            count += 1

            try:
                connection.close()  # closes a connection
                print("Connection #" + str(count) + " has successfully closed")
            except (socket_error, OSError, AttributeError):
                print("Connection #" + str(count) + " has failed to close")

        count = 0
        for open_socket in self.socks:  # iterates through all sockets
            count += 1

            try:
                self.socks[open_socket].close()  # closes a socket
                print("Socket #" + str(count) + " has successfully closed")
            except (socket_error, OSError, AttributeError):
                print("Socket #" + str(count) + " has failed to close")

    def trans_finn(self, cnts, packs, file=None):
        """
        Prints a message declaring that a program has completed a successful
        data file transfer and exits the program after closing the file
        """
        if len(cnts) == 2 and file is not None:
            file.close()  # closes the file being written to/read from
            time_str = stmt = ""
        else:
            l_prb, b_err, b_prb = str(cnts[2] * 100), str(cnts[4]), str(self.BIT_ERR * 100)
            tym, lst = str(round(cnts[5], 2)), str(cnts[3])
            time_str = " in " + tym + " seconds"
            stmt = ("\n - " + lst + " packets lost at a probability of " + l_prb + "%" +
                    "\n - " + b_err + " bit errors at a probability of " + b_prb + "%")

        print("\nSuccessful transmission of " + str(packs) + " packets" + time_str + ":\n - " +
              str(cnts[0]) + " transmissions sent \n - " +
              str(cnts[1]) + " transmissions received" + stmt + "\n")

        if file:
            print(str(file.name) + " has successfully closed")
        self.close_sockets_connections()  # closes sockets and connections
        print("TCP socket program: " + str(self.program).capitalize() + " has completed transmitting.")
        exit(1)  # exits the program

    def conn_error(self, file=None):
        """
        When connection error occurs, closes sockets and connections
        prints explanatory declarations, and exits the program
        """
        if file:
            file.close()  # closes the file being written to/read from
            print(str(file.name) + " has successfully closed")
        self.close_sockets_connections()  # closes sockets and connections
        print("\nA connection to another program has failed!")
        self.exit_program()  # exits the program

    def new_port(self, port):
        """
        Prompts a user to re-enter a valid integer value for a specified port
        """
        print("\nError! Port " + str(port) + " value " + str(self.ports[port]) +
              " is not a distinct integer value between " + str(self.MIN_RANGE) +
              " and " + str(self.MAX_RANGE) + ".")
        temp = input("Re-enter a valid " + str(port) + " value: ")
        temp = self.check_instance(temp, int)
        return temp

    def print_active_ports(self):
        """
        Prints the port names and respective port values for when entering
        a new port value due to either range or uniqueness test fail
        """
        print("\nPort values in use:")
        for port in self.ports:
            print("    " + str(port) + ": " + str(self.ports[port]))

    def in_range(self, port):
        """
        Checks that a provided integer value is within
        the range of the globals MIN_RANGE and MAX_RANGE
        """
        return self.MIN_RANGE <= port <= self.MAX_RANGE

    def port_socket_init(self):
        """
        Checks and ensures that input port values are distinct integers
        within a specified range. Then sets and binds sockets
        """
        for port in self.ports:
            item = self.ports[port]

            # iterates until port is a unique integer value >= 1024 and <= 64000
            while not self.in_range(item) or Counter(self.ports.values())[item] != 1:
                self.print_active_ports()  # prints all the port values in use
                self.ports[port] = int(self.new_port(port))
                item = self.ports[port]

            if port in self.socks.keys():
                # creates a socket
                try:
                    self.socks[port] = socket(AF_INET, SOCK_STREAM)

                    if port[-2:] == 'In':
                        # binds the created socket to its relevant port value
                        self.socks[port].bind((self.LOOPBACK, item))
                except socket_error:
                    self.conn_error()

    def print_data(self, raw_data, pack_num, length, count=0):
        """
        Prints data that has been successfully transmitted between programs
        """
        if count > 0:
            count = " after " + str(count) + " attempt(s)."
        else:
            count = "."
        print("\nData packet #" + str(pack_num) + " has successfully transmitted" +
              count + " " + str(length) + " char data packet contents:\n")

        if len(raw_data) == 0:  # if end of transfer acknowledgement packet
            data = "<empty packet>"  # declare the packet transferring is finished
            pack_num -= 1  # decrement packet count as its end of transfer packet
        else:
            try:
                data = raw_data.decode()  # data from the data packet as string text
            except UnicodeDecodeError:
                data = raw_data  # data from the transferred data packet in bytes

        for i in range(0, len(data), Packet.MAX_BYTES // self.PACKET_DATA_DIVISOR):  # iterate through data
            print(data[i:Packet.MAX_BYTES // self.PACKET_DATA_DIVISOR + i])  # print a line of up to 102 chars
        return pack_num + 1  # return an incremented count of packets sent

    def server_listen(self, sock, conn):
        """
        Listen for a socket connection
        """
        print("Listening for a socket connection to " + list(self.programs.keys())[self.programs_conn_counter] + "...")
        try:
            sock.listen(5)  # listens for a socket connection
        except socket_error:
            return conn
        return [1] + conn[:2]

    def server_accept(self, sock, conn):
        """
        Accept and return a socket connection
        """
        try:
            is_readable, _, _ = select([sock], [], [], 1)  # waits for input on socket

            if is_readable:
                connection, _ = sock.accept()  # accepts a socket connection
                print("In port for " + list(self.programs.keys())[self.programs_conn_counter] + " connected...")
                return connection, [1] + conn[:2]
        except socket_error:
            return sock, conn
        return sock, conn

    def client_connect(self, client, server, conn):
        """
        Connect client sockets to server sockets
        """
        while True:
            try:
                client.connect((self.LOOPBACK, server))  # connect to a port
            except socket_error:
                continue
            print("Out port for " + list(self.programs.keys())[self.programs_conn_counter] + " connected...")
            break
        return [1] + conn[:2]

    def conn_init(self):
        """
        Connect a programs sockets to other program sockets
        """
        print("\nWaiting for connection...")
        cnc, go, timer = [[0] * len(self.conns[0])] * len(self.conns), [1, 0], time()
        result = [None, None] if self.program == list(self.programs.keys())[0] else [None]
        dbl = False

        if len(self.conns) > 1:
            dbl = True

        while (time() - timer) < self.TIME_OUT and any(0 in stg for stg in cnc):
            for conn in self.conns:
                self.programs_conn_counter += 1 if self.program == list(self.programs.keys())[0] else 0
                self.programs_conn_counter = min(2, self.programs_conn_counter)

                pos = self.conns.index(conn)
                tmp = cnc[pos]

                if 0 in cnc[pos]:
                    if (1 not in tmp and dbl) or (tmp[:2] == go and not dbl):
                        cnc[pos] = self.server_listen(conn[0], cnc[pos])
                        tmp = cnc[pos]

                    if (tmp[:2] == go and dbl) or (tmp[-2:] == go and not dbl):
                        result[pos], cnc[pos] = self.server_accept(conn[0], cnc[pos])
                        tmp = cnc[pos]

                    if (tmp[-2:] == go and dbl) or (1 not in tmp and not dbl):
                        cnc[pos] = self.client_connect(conn[1], conn[2], cnc[pos])

        self.conns = result

        if not any(0 in stg for stg in cnc):
            print("All sockets are connected\n\nTransmission status report: ")
            return timer
        self.conn_error()  # closes when connecting fails

    def check_instance(self, val, instance):
        """
        Checks if a value is the specified instance, otherwise exits program.
        """
        try:
            return instance(val)
        except (TypeError, ValueError):
            self.exit_program()

    def send_packet(self, port, packet, check_sum, file):
        """

        """
        try:
            self.socks[port].send(packet.buffer(check_sum))
        except (socket_error, ConnectionError):
            self.conn_error(file)  # close program

    def receive_packet(self, fails, offset, file):
        """

        """
        try:
            received_packet, _ = Packet.un_buffer(self.conns[0].recv(self.BUFFER))
            return received_packet, 0, None
        except (socket_error, struct_error, ValueError) as error:
            if fails == 0:
                self.print_invalid_packet(list(self.programs.keys()).index(self.program) + offset)
            elif fails > self.TIME_OUT:  # connection is deemed lost
                self.conn_error(file)  # close program
            fails += 1  # increment number of failed socket readings
            return None, fails, error

    def print_invalid_packet(self, sender_program):
        """

        """
        print("\nReceived packet from " + list(self.programs.keys())[sender_program] + " is invalid. Packet dropped.")

    def validate_args(self, arguments, required_length, types):
        print(types)
        if len(arguments) < required_length:
            self.exit_program()
        return [self.check_instance(argument, typ) for argument, typ in zip(arguments[1:required_length], types)]


def main(arguments):
    if len(arguments) == 3:
        f, p, port = arguments[1], arguments[2], [str(i) for i in rs(range(1024, 6400), 8)]
        commands = {
            "python3 channel.py " + port[0] + " " + port[1] + " " + port[2] + " " +
            port[3] + " " + port[4] + " " + port[5] + " " + p,
            "python3 receiver.py " + port[5] + " " + port[6] + " " + port[2] + " received_" + f,
            "python3 sender.py " + port[4] + " " + port[7] + " " + port[0] + " " + f
        }

        for command in commands:
            terminal(f"xfce4-terminal --hold --command='{command}' &")
            print("Executed " + command.split()[1])
    else:
        print("Error! Must enter: python3 tcp_transmission.py <file> <float>")


if __name__ == '__main__':
    main(argv)
