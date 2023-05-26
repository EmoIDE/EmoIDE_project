from re import S
import socket
import time
import re
import neurokit2 as nk

class E4:
    """
    An E4 object that can connect to an E4 device and recieve data from that device
    """

    def __init__(self, ip :str, port : int) -> None:
        """
        Initalizes the E4 object.

        Args:
            ip (str): The IP of the extension server.
            port (int): The port to the #4 streaming server application.
        """

        self.server_ip = ip
        self.server_port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   

        self.EDA_signal = []
        self.EDA_timer = 0


    def E4_SS_connect(self):
        """
        Establishes a connection with an available E4 device connected to the E4 streaming server on the specified port.
        
        Raises:
            Exception: If any exception occurs when trying to connect to the E4 streaming server.
        """

        try:
            self.client_socket.connect((self.server_ip, self.server_port))

            self.client_socket.send(('device_discover_list \n'.encode("utf-8")))      # "command".encode() ALT. bytes("command", "utf-8")
            msg = self.client_socket.recv(256)
            print(msg.decode("utf-8"))

            self.client_socket.send('device_connect_btle 082FCD\n'.encode("utf-8"))     # 082FCD is a specific unit
            msg = self.client_socket.recv(256)
            print(msg.decode("utf-8"))

            self.client_socket.send('device_list \n'.encode("utf-8"))
            msg = self.client_socket.recv(256)
            print(msg.decode("utf-8"))

            self.client_socket.send('device_connect 082FCD\n'.encode("utf-8"))
            msg = self.client_socket.recv(256)
            print(msg.decode("utf-8"))

        except:
            print("[ERROR] - Connection to E4 Streaming Server failed")
        
    def start_subscriptions(self):
        """
        Starts subscribing to a data stream for the BVP, IBI, and GSR from the connected device.

        Raises:
            Exception: If any exception occurs while trying to subscribe to data stream.
        """

        requests = ['device_subscribe bvp ON\n', 'device_subscribe ibi ON\n', 'device_subscribe gsr ON\n']

        try:
            for i in requests:
                # send
                self.client_socket.send(i.encode("utf-8"))
                # recive
                rec = self.client_socket.recv(2048)
                print(rec.decode("utf-8"))
        except:
            print("[ERROR] - Can not subscribe to stream")
    
    def recieve_data(self):
        """
        Receives data from the connected E4 device and returns the last given values of each type.

        Raises:
            Exception: If any exception occurs while trying to exctract data from subscribed data stream
        """

        msg_arr = []
        start = time.time()
        delta = 0
        self.client_socket.settimeout(5.0)      # stops .recv after 5s if no msg is recived
        while delta < 1:
            try:
                msg_arr.append(self.client_socket.recv(2048).decode("utf-8"))
            except:
                print("[ERROR] - no message recived from e4 Streaming Server")
            delta = time.time() - start
        return self.get_latest_values(msg_arr)

    def e4_stop(self):
        """
        Ends all data streaming subscriptions to the device and disconnects the device from the application.

        Raises:
            ConnectionError: If there is an error stopping the data subscriptions or disconnecting from the E4 device.
        """
        
        requests = ['device_subscribe bvp OFF\n', 'device_subscribe ibi OFF\n', 'device_subscribe gsr OFF\n']
        try:
            for i in requests:
                # send
                self.client_socket.send(i.encode("utf-8"))

                # recive
                rec = self.client_socket.recv(2048)
                print(rec.decode("utf-8"))

        finally:
            print("DATA SUBSCRIPTION OFF")
        
        self.client_socket.send('device_disconnect\n'.encode("utf-8"))
        print("e4 disconnected")

    def get_latest_values(self, arr):
        """
        Receives a list of string values in the format "value-type time value" and returns the last value in the list of each type.
        The function also processes the GSR value and returns tonic and phasic values based on the GSR values.

        Args:
            arr (list): A list of string values in the format "value-type time value".

        Returns:
            list: A list with the last value in the list of each type.

        Raises:
            ValueError: If the provided list does not contain valid data values.
        """

        fixed_arr = []
        for i in arr:
            end_of_id = i.find(" ")
            id = i[0 : end_of_id]
            
            try:
                pattern = r'-?\d+,\d+(?=\r\n$)'  # Matches a float followed by \r\n at the end of the string
                result = re.findall(pattern, i)
                last_float = result[0]
            except:
                print("[ERROR] - e4 data not available")
            
            if id == "E4_Hr":
                data_and_name = "Hr:" + last_float
                fixed_arr.append(data_and_name)
            elif id == "E4_Bvp":
                data_and_name = "Bvp:" + last_float
                fixed_arr.append(data_and_name)
            elif id == "E4_Gsr":
                data_and_name = "Gsr:" + last_float
                fixed_arr.append(data_and_name)
            
        # filter array
        hr, bvp, gsr = "", "", ""
        for j in fixed_arr:
            end_of_id = j.find(":")
            id = j[0 : end_of_id]

            if id == "Hr":
                hr = j
            elif id == "Bvp":
                bvp = j
            elif id == "Gsr":
                gsr = j
        
        if time.time() - self.EDA_timer > 0.5 and gsr != "":

            gsr_string = gsr[gsr.find(":")+1:]
            self.EDA_signal.append(float(gsr_string.replace(",", ".")))
            self.EDA_timer = time.time()

        ret_arr = [hr, bvp, gsr]


        return ret_arr