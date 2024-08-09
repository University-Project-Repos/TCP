# COSC264 TCP Networking Assignment

Transmission Control Protocol (TCP) simulation for sequential byte file communication between sender, 
receiver and network channel socket interfaces 
with an expected packet loss rate of `N/((1-P)(1-P))`, 
where `N` is bit errors for each byte packet transmitted, and `P` is the independent packet loss probability.

### Team

* [Adam Ross](https://github.com/r055a)
* Helen Yang

# Instructions

## Requirements

- Python3

## Run


 * `input-file` is for transmitting and must exist, preferably with data
 * `P` is the probability of packet loss and is required to be between `0.0` and `0.99`

The following command will open terminals for simulating TCP file transmission on a local network:
```bash
python3 tcp_transmission.py <input-file (str)> <P (float)>
```

 Alternatively, the following can be executed in any sequence using a separate terminal for each:
 
 ```bash
 python3 channel.py <csIn (int)> <csOut (int)> <crIn (int)> <crOut (int)> <sIn (int)> <rIn (int)> <P (float)>
 ```
 
 ```bash
 python3 receiver.py <rIn (int)> <rOut (int)> <crIn (int)> <output-file (str)>
 ```
 
 ```bash
 python3 sender.py <sIn (int)> <sOut (int)> <csIn (int)> <input-file (str)>
 ```
 
 * Each unique `<port (int)>` value must be a unique integer between `1024` and `64_000`
 * `crIn` and `csIn` must match between `channel.py` and `receiver.py` and `sender.py`, respectively

# Example

The following is an example where `"hello world!"` is transmitted with `N = 0.1` and `P = 0.5`:

## Channel program output

```
Waiting for connection...
Listening for a socket connection to receiver...
In port for receiver connected...
Out port for receiver connected...
Listening for a socket connection to sender...
In port for sender connected...
Out port for sender connected...
All sockets are connected

Transmission status report:
Data packet containing 12 chars transmitted from sender
Data packet containing 12 chars transmitted to receiver
Acknowledgement packet containing 0 chars transmitted from receiver
A μ value of 0.1858 < 0.5, indicating #1 occurrence of the probability of a packet loss event
Data packet containing 12 chars transmitted from sender
A μ value of 0.2151 < 0.5, indicating #2 occurrence of the probability of a packet loss event
Data packet containing 12 chars transmitted from sender
A μ value of 0.0245 < 0.5, indicating #3 occurrence of the probability of a packet loss event
Data packet containing 12 chars transmitted from sender
A μ value of 0.1253 < 0.5, indicating #4 occurrence of the probability of a packet loss event
Data packet containing 12 chars transmitted from sender
Data packet containing 12 chars transmitted to receiver
Acknowledgement packet containing 0 chars transmitted from receiver
Acknowledgement packet containing 0 chars transmitted to sender
Data packet containing 0 chars transmitted from sender
Data packet containing 0 chars transmitted to receiver
Acknowledgement packet containing 0 chars transmitted from receiver
Acknowledgement packet containing 0 chars transmitted to sender
All TCP transmissions are complete

Successful transmission of 0 packets in 4.01 seconds:
 - 9 transmissions sent
 - 9 transmissions received
 - 4 packets lost at a probability of 50.0%
 - 0 bit errors at a probability of 10.0%

Connection #1 has successfully closed
Connection #2 has successfully closed
Socket #1 has successfully closed
Socket #2 has successfully closed
Socket #3 has successfully closed
Socket #4 has successfully closed
TCP socket program: Channel has completed transmitting.
```

## Receiver program output

```
Waiting for connection...
Out port for channel connected...
Listening for a socket connection to channel...
In port for channel connected...
All sockets are connected

Transmission status report:

Data packet #1 has successfully transmitted. 12 char data packet contents:

hello world!

Data packet #2 has successfully transmitted. 0 char data packet contents:

<empty packet>

Successful transmission of 2 packets:
 - 3 transmissions sent
 - 3 transmissions received

received_input.txt has successfully closed
Connection #1 has successfully closed
Socket #1 has successfully closed
Socket #2 has successfully closed
TCP socket program: Receiver has completed transmitting.
```

## Sender program output

```
Waiting for connection...
Out port for channel connected...
Listening for a socket connection to channel...
In port for channel connected...
All sockets are connected

Transmission status report:

Data packet #1 has successfully transmitted after 5 attempt(s). 12 char data packet contents:

hello world!

Data packet #2 has successfully transmitted after 1 attempt(s). 0 char data packet contents:

<empty packet>

Successful transmission of 2 packets:
 - 6 transmissions sent
 - 2 transmissions received

input.txt has successfully closed
Connection #1 has successfully closed
Socket #1 has successfully closed
Socket #2 has successfully closed
TCP socket program: Sender has completed transmitting.
```
