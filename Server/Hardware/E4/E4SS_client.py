from re import S
import socket
import time


#Hur man skriver pause eller unpause
# client_socket.send('pause ON\n'.encode("utf-8"))
# client_socket.send('pause OFF\n'.encode("utf-8"))


# Create a connection to the server application
# Connection
server_ip = '127.0.0.1'
server_port = 28000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # tcp socket är en steam of data
# '\r\n' !!!! End with newline: '\n'

try:

    client_socket.connect((server_ip, server_port))

    client_socket.send(('device_discover_list \n'.encode("utf-8")))      # "command".encode() ALT. bytes("command", "utf-8")
    msg = client_socket.recv(256)
    print(msg.decode("utf-8"))

    client_socket.send('device_connect_btle 082FCD\n'.encode("utf-8"))
    msg = client_socket.recv(256)
    print(msg.decode("utf-8"))

    client_socket.send('device_list \n'.encode("utf-8"))
    msg = client_socket.recv(256)
    print(msg.decode("utf-8"))

    client_socket.send('device_connect 082FCD\n'.encode("utf-8"))
    msg = client_socket.recv(256)
    print(msg.decode("utf-8"))

finally:
    print("CLIENT CONNECTION DONE")


### Get values
# bvp = Bloode Volume Pulse
# gsr = Galvanic Skin Response
# ibi = Inter Beat Interval and Hearbeat
# acc = 3-axis Acceleration

#requests = ['device_subscribe gsr ON', 'device_subscribe bvp ON', 'device_subscribe ibi ON', 'device_subscribe acc ON', 'device_subscribe bat ON']
# data requests
#requests = ['device_subscribe gsr ON\n', 'device_subscribe bvp ON\n', 'device_subscribe ibi ON\n', 'device_subscribe acc ON\n', 'device_subscribe bat ON\n']
requests = ['device_subscribe bvp ON\n']
try:
    for i in requests:
        # send
        client_socket.send(i.encode("utf-8"))
        # recive
        rec = client_socket.recv(256)
        print(rec.decode("utf-8"))

finally:
    print("REQUESTS DONE")
    client_socket.send('pause OFF\n'.encode("utf-8"))
    print(client_socket.recv(256).decode("utf-8"))

####### OVAN OK

# Data collection
i = 0
while (i < 10):
    data = client_socket.recv(256).decode("utf-8")
    print(data)
    print("-----------------------------------------------\n")
    if len(data) > 0:
        i += 1


# Close connection
client_socket.close()


