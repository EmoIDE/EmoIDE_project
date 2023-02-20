from re import S
import socket


# Create a connection to the server application
# Connection
server_ip = '127.0.0.1'
server_port = 27100
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # tcp socket är en steam of data
# connection_send = ['devicelist', 'device_connect 082fcd']

# '\r\n' !!!! End with newline: '\n'

try:
    client_socket.connect((server_ip, server_port))
    client_socket.send(('device_connect_btle A01A16\n'.encode("utf-8")))      # "command".encode() ALT. bytes("command", "utf-8")
    msg = client_socket.recv(256)
    print(msg.decode("utf-8"))
        

finally:
    print("CLIENT CONNECTION")


# data requests
requests = ['device_subscribe gsr ON\n', 'device_subscribe bvp ON\n', 'device_subscribe ibi ON\n', 'device_subscribe acc ON\n', 'device_subscribe bat ON\n']
try:
    for i in requests:
        # send
        client_socket.send(i.encode("utf-8"))
        # recive
        data = client_socket.recv(256)
        print(data.decode("utf-8"))

finally:
    print("Done")








### Get values
# bvp = Bloode Volume Pulse
# gsr = Galvanic Skin Response
# ibi = Inter Beat Interval and Hearbeat
# acc = 3-axis Acceleration
#requests = ['device_subscribe gsr ON', 'device_subscribe bvp ON', 'device_subscribe ibi ON', 'device_subscribe acc ON', 'device_subscribe bat ON']

"""
try:
    for i in requests:
        tcp_socket.sendall(i.encode())
    print("SS")

finally:
    print("Closing socket")
    tcp_socket.close()
"""








#########################################################################

"""
# Create a connection to the server application on port 81

# bvp = Bloode Volume Pulse
# gsr = Galvanic Skin Response
# ibi = Inter Beat Interval and Hearbeat
# acc = 3-axis Acceleration
tcp_socket = socket.create_connection(('127.0.0.1', 28000))
requests = ['devicelist', 'device_connect 082fcd', 'device_subscribe gsr ON', 'device_subscribe bvp ON', 'device_subscribe ibi ON', 'device_subscribe acc ON', 'device_subscribe bat ON']

try:
    for i in requests:
        data = str.encode(i)
        tcp_socket.sendall(data)
    print("SS")

finally:
    print("Closing socket")
    tcp_socket.close()

"""



