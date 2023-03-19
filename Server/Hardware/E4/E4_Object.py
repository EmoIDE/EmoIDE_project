from re import S
import socket
import time

class E4:
    def __init__(self, ip :str, port : int) -> None:
        self.server_ip = ip
        self.server_port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
            # tcp socket är en steam of data


    def E4_SS_connect(self):
        try:
            #Kan ta bort alla prints här när vi väl får det att fungera
            self.client_socket.connect((self.server_ip, self.server_port))

            self.client_socket.send(('device_discover_list \n'.encode("utf-8")))      # "command".encode() ALT. bytes("command", "utf-8")
            msg = self.client_socket.recv(256)
            print(msg.decode("utf-8"))

            self.client_socket.send('device_connect_btle 082FCD\n'.encode("utf-8"))
            msg = self.client_socket.recv(256)
            print(msg.decode("utf-8"))

            self.client_socket.send('device_list \n'.encode("utf-8"))
            msg = self.client_socket.recv(256)
            print(msg.decode("utf-8"))

            self.client_socket.send('device_connect 082FCD\n'.encode("utf-8"))
            msg = self.client_socket.recv(256)
            print(msg.decode("utf-8"))

        finally:
            print("CLIENT CONNECTION DONE")
        
    def start_subscriptions(self):
        requests = ['device_subscribe gsr ON\n', 'device_subscribe bvp ON\n', 'device_subscribe ibi ON\n', 'device_subscribe acc ON\n']

        try:
            for i in requests:
                # send
                self.client_socket.send(i.encode("utf-8"))
                # recive
                rec = self.client_socket.recv(256)
                print(rec.decode("utf-8"))

        finally:
            print("REQUESTS DONE")
            self.client_socket.send('pause OFF\n'.encode("utf-8"))
            print(self.client_socket.recv(256).decode("utf-8"))

e4 = E4('127.0.0.1', 28000)

e4.E4_SS_connect()
e4.start_subscriptions()