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
            #Kan ta bort alla prints här när vi väl får det att fungera
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
            #print("msg_arr:  ", msg_arr)
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
                a = 1+1
                #print("[ERROR] - e4 data not available")
            
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
        
        # print(gsr)
        if time.time() - self.EDA_timer > 0.5 and gsr != "":

            gsr_string = gsr[gsr.find(":")+1:]
            self.EDA_signal.append(float(gsr_string.replace(",", ".")))
            #if len(self.EDA_signal) > 10:
                #signals, info = nk.eda_process(self.EDA_signal, sampling_rate=2)
                #cleaned = signals["EDA_Clean"]
                # print(type(cleaned))
                # print(cleaned)
                #data = nk.eda_phasic(nk.standardize(cleaned), sampling_rate=2)
                # print(type(data))
                # print(data)
            self.EDA_timer = time.time()

        ret_arr = [hr, bvp, gsr]


        return ret_arr
    
# if __name__ == "__main__":
#     pass
    # arr = ['E4_Bvp 1680442024,64479 21,54169\r\n', 'E4_Bvp 1680442024,66041 20,6037\r\n', 'E4_Bvp 1680442024,67604 18,71289\r\n', 'E4_Bvp 1680442024,69167 16,2948\r\n', 'E4_Bvp 1680442024,70729 13,88983\r\n', 'E4_Bvp 1680442024,72292 11,95648\r\n', 'E4_Bvp 1680442024,73854 10,80438\r\nE4_Bvp 1680442024,75417 10,45679\r\n', 'E4_Bvp 1680442024,76979 10,6615\r\n', 'E4_Bvp 1680442024,78542 10,90839\r\n', 'E4_Bvp 1680442024,80105 10,54761\r\n', 'E4_Bvp 1680442024,81667 9,069153\r\n', 'E4_Bvp 1680442024,8323 6,348389\r\n', 'E4_Bvp 1680442024,84792 2,764038\r\n', 'E4_Bvp 1680442024,86355 -0,9607544\r\n', 'E4_Bvp 1680442024,87917 -4,086426\r\n', 'E4_Bvp 1680442024,8948 -6,227966\r\n', 'E4_Bvp 1680442024,91043 -7,482361\r\nE4_Bvp 1680442024,92605 -8,306152\r\n', 'E4_Bvp 1680442024,94168 -9,220825\r\n', 'E4_Bvp 1680442024,9573 -10,54736\r\n', 'E4_Bvp 1680442024,97293 -12,31921\r\n', 'E4_Bvp 1680442024,98855 -14,46472\r\n', 'E4_Bvp 1680442025,00418 -17,05902\r\n', 'E4_Bvp 1680442025,01981 -20,39124\r\n', 
    # 'E4_Bvp 1680442025,03543 -24,83392\r\n', 'E4_Bvp 1680442025,05106 -30,44464\r\n', 'E4_Bvp 1680442025,06668 -36,70984\r\n', 'E4_Bvp 1680442025,08231 -42,50568\r\n', 'E4_Bvp 1680442025,09793 -46,45209\r\n', 'E4_Bvp 1680442025,11356 -47,43671\r\n', 'E4_Bvp 1680442025,12919 -45,03082\r\n', 'E4_Bvp 1680442025,14481 -39,61743\r\n', 'E4_Bvp 1680442025,16044 -32,20575\r\n', 'E4_Bvp 1680442025,17606 -23,97302\r\n', 'E4_Bvp 1680442025,19169 -15,91724\r\n', 'E4_Bvp 1680442025,20731 -8,542419\r\n', 'E4_Bvp 1680442025,22294 -2,003601\r\n', 'E4_Bvp 1680442025,23857 3,802612\r\n', 'E4_Bvp 1680442025,25419 8,952087\r\n', 'E4_Hr 1680442019,71662 61,93262\r\n', 'E4_Ibi 1680442019,71662 0,9687948\r\n', 'E4_Bvp 1680442025,26982 13,36218\r\n', 'E4_Bvp 1680442025,28544 16,8562\r\n', 'E4_Bvp 1680442025,30107 19,23303\r\n', 
    # 'E4_Bvp 1680442025,31669 20,3819\r\n', 'E4_Bvp 1680442025,33232 20,38782\r\n', 'E4_Bvp 1680442025,34795 19,4964\r\n', 'E4_Bvp 1680442025,36357 18,06506\r\n', 'E4_Bvp 1680442025,3792 16,55524\r\n', 'E4_Bvp 1680442025,39482 15,39624\r\n', 'E4_Bvp 1680442025,41045 14,91235\r\n', 'E4_Bvp 1680442025,42607 15,17395\r\nE4_Bvp 1680442025,4417 15,99048\r\n', 'E4_Bvp 1680442025,45733 16,97015\r\n', 'E4_Bvp 1680442025,47295 17,72656\r\n', 'E4_Bvp 1680442025,48858 18,07843\r\n', 'E4_Bvp 1680442025,5042 18,07684\r\n', 'E4_Bvp 1680442025,51983 17,96753\r\n', 'E4_Bvp 1680442025,53546 17,99316\r\n', 'E4_Bvp 1680442025,55108 18,22925\r\n', 'E4_Bvp 1680442025,56671 18,57397\r\n', 'E4_Bvp 1680442025,58233 18,84863\r\n', 'E4_Bvp 1680442025,59796 18,8736\r\nE4_Bvp 1680442025,61358 18,52783\r\n', 'E4_Bvp 1680442025,62921 17,68158\r\n', 'E4_Bvp 1680442025,64484 16,18591\r\n', 'E4_Bvp 1680442025,66046 13,89734\r\n', 'E4_Bvp 1680442025,67609 10,87469\r\n', 'E4_Bvp 1680442025,69171 7,508789\r\n', 'E4_Bvp 1680442025,70734 4,416077\r\n', 'E4_Bvp 1680442025,72296 2,253662\r\n', 'E4_Bvp 1680442025,73859 1,318542\r\n', 'E4_Bvp 1680442025,75422 1,402527\r\n', 'E4_Bvp 1680442025,76984 1,810303\r\nE4_Bvp 1680442025,78547 1,677795\r\nE4_Bvp 1680442025,80109 0,3630981\r\n', 'E4_Bvp 1680442025,81672 -2,345581\r\n', 'E4_Bvp 1680442025,83234 -6,116028\r\n', 'E4_Bvp 1680442025,84797 -10,31799\r\n', 'E4_Bvp 1680442025,8636 -14,22076\r\n', 'E4_Bvp 1680442025,87922 -17,30035\r\n', 'E4_Bvp 1680442025,89485 -19,37018\r\n', 'E4_Bvp 1680442025,91047 -20,57465\r\n', 'E4_Gsr 1680442024,73 0,0832364\r\n', 'E4_Gsr 1680442024,98 0,07939473\r\nE4_Gsr 1680442025,23 0,07939473\r\n', 'E4_Gsr 1680442025,48 0,07939473\r\n', 'E4_Gsr 1680442025,73 0,07939473\r\n', 'E4_Gsr 1680442025,98 0,0832364\r\n', 'E4_Bvp 1680442025,9261 -21,35791\r\n', 'E4_Bvp 1680442025,94172 -22,30878\r\n', 'E4_Bvp 1680442025,95735 -24,00647\r\n', 'E4_Bvp 1680442025,97298 -26,86639\r\n', 'E4_Bvp 1680442025,9886 -30,9787\r\n', 'E4_Bvp 1680442026,00423 -35,96234\r\n', 'E4_Bvp 1680442026,01985 -41,05048\r\n', 'E4_Bvp 1680442026,03548 -45,10626\r\n', 'E4_Bvp 1680442026,0511 -46,94904\r\n', 'E4_Bvp 1680442026,06673 -45,62817\r\n', 'E4_Bvp 1680442026,08236 -40,75385\r\n', 'E4_Bvp 1680442026,09798 -32,69067\r\n', 'E4_Bvp 1680442026,11361 -22,4931\r\n', 'E4_Bvp 1680442026,12923 -11,66394\r\n', 'E4_Bvp 1680442026,14486 -1,659485\r\n', 'E4_Bvp 1680442026,16048 6,413208\r\n', 'E4_Bvp 1680442026,17611 12,06921\r\n', 'E4_Hr 1680442020,60729 67,3653\r\n', 'E4_Ibi 1680442020,60729 0,8906662\r\n', 'E4_Bvp 1680442026,19174 15,40839\r\n', 'E4_Bvp 1680442026,20736 16,96246\r\n', 'E4_Bvp 1680442026,22299 17,42041\r\n', 'E4_Bvp 1680442026,23861 17,43842\r\n', 'E4_Bvp 1680442026,25424 17,47198\r\n', 'E4_Bvp 1680442026,26986 17,73975\r\n', 'E4_Bvp 1680442026,28549 18,32288\r\nE4_Bvp 1680442026,30112 19,14551\r\n', 'E4_Bvp 1680442026,31674 20,11981\r\n', 'E4_Bvp 1680442026,33237 21,16943\r\n', 'E4_Bvp 1680442026,34799 22,15924\r\n', 'E4_Bvp 1680442026,36362 22,90521\r\n', 'E4_Bvp 1680442026,37924 23,20782\r\n', 'E4_Bvp 1680442026,39487 22,99744\r\n', 'E4_Bvp 1680442026,4105 22,49298\r\n', 'E4_Bvp 1680442026,42612 22,15485\r\n', 'E4_Bvp 1680442026,44175 22,52045\r\n', 'E4_Bvp 1680442026,45737 23,86133\r\nE4_Bvp 1680442026,473 25,94873\r\n', 'E4_Bvp 1680442026,48862 28,0329\r\n', 'E4_Bvp 1680442026,50425 29,1629\r\n', 'E4_Bvp 1680442026,51988 28,62274\r\n', 'E4_Bvp 1680442026,5355 26,26038\r\n', 'E4_Bvp 1680442026,55113 22,5946\r\n', 'E4_Bvp 1680442026,56675 18,52496\r\n', 'E4_Bvp 1680442026,58238 14,93781\r\n', 'E4_Bvp 1680442026,598 12,4411\r\n', 'E4_Bvp 1680442026,61363 11,18829\r\n', 'E4_Bvp 1680442026,62926 10,96326\r\nE4_Bvp 1680442026,64488 11,32214\r\n', 'E4_Bvp 1680442026,66051 11,73462\r\n', 'E4_Bvp 1680442026,67613 11,73309\r\n', 'E4_Bvp 1680442026,69176 10,96088\r\n', 'E4_Bvp 1680442026,70738 9,303589\r\n', 'E4_Bvp 1680442026,72301 6,904663\r\n', 'E4_Bvp 1680442026,73864 4,163513\r\n', 'E4_Bvp 1680442026,75426 1,523682\r\n', 'E4_Bvp 1680442026,76989 -0,6876221\r\n', 'E4_Bvp 1680442026,78551 -2,371582\r\n', 'E4_Bvp 1680442026,80114 -3,749512\r\n', 'E4_Bvp 1680442026,81676 -5,159119\r\n', 'E4_Bvp 1680442026,83239 -6,887329\r\n', 'E4_Bvp 1680442026,84802 -9,03241\r\n', 'E4_Bvp 1680442026,86364 -11,51331\r\n', 'E4_Bvp 1680442026,87927 -14,16333\r\n', 'E4_Bvp 1680442026,89489 -16,90472\r\n', 'E4_Bvp 1680442026,91052 -19,77692\r\n', 'E4_Bvp 1680442026,92614 -22,90076\r\n', 'E4_Bvp 1680442026,94177 -26,41608\r\n', 'E4_Bvp 1680442026,9574 -30,38367\r\n', 'E4_Bvp 1680442026,97302 -34,68817\r\n', 'E4_Bvp 1680442026,98865 -39,09644\r\n', 'E4_Bvp 1680442027,00427 -43,30231\r\n', 'E4_Bvp 1680442027,0199 -46,92749\r\n', 'E4_Bvp 1680442027,03552 -49,48419\r\n', 'E4_Bvp 1680442027,05115 -50,46082\r\n', 'E4_Bvp 1680442027,06678 -49,27478\r\n', 'E4_Bvp 1680442027,0824 -45,58813\r\n', 'E4_Bvp 1680442027,09803 -39,38141\r\n', 'E4_Bvp 1680442027,11365 -31,1037\r\n', 'E4_Bvp 1680442027,12928 -21,60901\r\n', 'E4_Bvp 1680442027,1449 -11,98083\r\n', 'E4_Bvp 1680442027,16053 -3,212769\r\n', 'E4_Bvp 1680442027,17616 4,044495\r\n', 'E4_Bvp 1680442027,19178 9,599915\r\n', 'E4_Bvp 1680442027,20741 13,66949\r\n', 'E4_Hr 1680442021,52921 65,08173\r\n', 'E4_Ibi 1680442021,52921 0,9219177\r\n', 'E4_Bvp 1680442027,22303 16,61493\r\n', 'E4_Bvp 1680442027,23866 18,72968\r\n', 'E4_Bvp 1680442027,25428 20,07513\r\n', 'E4_Bvp 1680442027,26991 20,56641\r\n', 'E4_Bvp 1680442027,28554 20,15521\r\n', 'E4_Bvp 1680442027,30116 19,03729\r\n', 'E4_Bvp 1680442027,31679 17,67065\r\nE4_Bvp 1680442027,33241 16,63831\r\n', 'E4_Bvp 1680442027,34804 16,47864\r\n', 'E4_Bvp 1680442027,36366 17,39417\r\n', 'E4_Bvp 1680442027,37929 19,23804\r\n', 'E4_Bvp 1680442027,39492 21,57458\r\n', 'E4_Bvp 1680442027,41054 23,86066\r\n', 'E4_Bvp 1680442027,42617 25,66876\r\n', 'E4_Bvp 1680442027,44179 26,79718\r\n', 'E4_Bvp 1680442027,45742 27,3222\r\n', 'E4_Gsr 1680442026,23 0,07939473\r\n', 'E4_Gsr 1680442026,48 0,07939473\r\n', 'E4_Gsr 1680442026,73 0,08195585\r\n', 'E4_Gsr 1680442026,98 0,07939473\r\n', 'E4_Gsr 1680442027,23 0,08195585\r\n', 'E4_Gsr 1680442027,48 0,0832364\r\n', 'E4_Bvp 1680442027,47304 27,46204\r\n', 'E4_Bvp 1680442027,48867 27,49677\r\n', 'E4_Bvp 1680442027,5043 27,5119\r\n', 'E4_Bvp 1680442027,51992 27,36707\r\n', 'E4_Bvp 1680442027,53555 26,78674\r\n', 'E4_Bvp 1680442027,55117 25,51404\r\n', 'E4_Bvp 1680442027,5668 23,53119\r\n', 'E4_Bvp 1680442027,58242 21,09229\r\n', 'E4_Bvp 1680442027,59805 18,58423\r\n', 'E4_Bvp 1680442027,61368 16,30518\r\n', 'E4_Bvp 1680442027,6293 14,34027\r\n', 'E4_Bvp 1680442027,64493 12,56946\r\n', 'E4_Bvp 1680442027,66055 10,84698\r\n', 'E4_Bvp 1680442027,67618 9,131104\r\n', 'E4_Bvp 1680442027,6918 7,520142\r\n', 'E4_Bvp 1680442027,70743 6,156677\r\n', 'E4_Bvp 1680442027,72306 5,074524\r\n', 'E4_Bvp 1680442027,73868 4,195129\r\n', 'E4_Bvp 1680442027,75431 3,335876\r\n', 'E4_Bvp 1680442027,76993 2,388794\r\n', 'E4_Bvp 1680442027,78556 1,330078\r\n', 'E4_Bvp 1680442027,80119 0,2666626\r\n', 'E4_Bvp 1680442027,81681 -0,7248535\r\n', 'E4_Bvp 1680442027,83244 -1,636475\r\n', 'E4_Bvp 1680442027,84806 -2,553406\r\n', 'E4_Bvp 1680442027,86369 -3,653198\r\n', 'E4_Bvp 1680442027,87931 -5,122375\r\n', 'E4_Bvp 1680442027,89494 -7,120422\r\n', 'E4_Bvp 1680442027,91057 -9,673828\r\n', 'E4_Bvp 1680442027,92619 -12,6933\r\n', 'E4_Bvp 1680442027,94182 -15,92487\r\n', 'E4_Bvp 1680442027,95744 -19,03351\r\n', 'E4_Bvp 1680442027,97307 -21,72186\r\n', 'E4_Bvp 1680442027,98869 -23,88306\r\n', 'E4_Bvp 1680442028,00432 -25,67535\r\n', 'E4_Bvp 1680442028,01995 -27,5224\r\n', 'E4_Bvp 1680442028,03557 -29,98236\r\n', 'E4_Bvp 1680442028,0512 -33,50739\r\n', 'E4_Bvp 1680442028,06682 -38,24323\r\n', 'E4_Bvp 1680442028,08245 -43,88641\r\n', 'E4_Bvp 1680442028,09807 -49,65814\r\n', 'E4_Bvp 1680442028,1137 -54,43481\r\n', 'E4_Bvp 1680442028,12933 -56,99731\r\n', 'E4_Bvp 1680442028,14495 -56,4295\r\n', 'E4_Bvp 1680442028,16058 -52,38104\r\n', 'E4_Bvp 1680442028,1762 -45,26428\r\nE4_Bvp 1680442028,19183 -36,13977\r\n', 'E4_Bvp 1680442028,20745 -26,33539\r\n', 'E4_Bvp 1680442028,22308 -17,02209\r\n', 'E4_Bvp 1680442028,23871 -8,952026\r\n', 'E4_Bvp 1680442028,25433 -2,337036\r\n', 'E4_Bvp 1680442028,26996 2,968933\r\n', 'E4_Bvp 1680442028,28558 7,234253\r\n', 'E4_Bvp 1680442028,30121 10,6814\r\n', 'E4_Hr 1680442022,56051 58,17913\r\n', 'E4_Ibi 1680442022,56051 1,031298\r\n', 'E4_Bvp 1680442028,31683 13,42639\r\n', 'E4_Bvp 1680442028,33246 15,48779\r\n', 'E4_Bvp 1680442028,34809 16,93604\r\nE4_Bvp 1680442028,36371 17,87268\r\n', 'E4_Bvp 1680442028,37934 18,39709\r\n', 'E4_Bvp 1680442028,39496 18,60919\r\n', 'E4_Bvp 1680442028,41059 18,5921\r\n', 'E4_Bvp 1680442028,42621 18,5025\r\n', 'E4_Bvp 1680442028,44184 18,58704\r\n', 'E4_Bvp 1680442028,45747 19,17645\r\n', 'E4_Bvp 1680442028,47309 20,53961\r\n', 'E4_Bvp 1680442028,48872 22,7063\r\n', 'E4_Bvp 1680442028,50434 25,43567\r\n', 'E4_Bvp 1680442028,51997 28,21204\r\nE4_Bvp 1680442028,53559 30,43719\r\n', 'E4_Bvp 1680442028,55122 31,63226\r\n', 'E4_Bvp 1680442028,56685 31,64465\r\n', 'E4_Bvp 1680442028,58247 30,61279\r\n', 'E4_Bvp 1680442028,5981 28,83881\r\n', 'E4_Bvp 1680442028,61372 26,68158\r\n', 'E4_Bvp 1680442028,62935 24,414\r\n', 'E4_Bvp 1680442028,64497 22,25195\r\n', 'E4_Bvp 1680442028,6606 20,41455\r\n', 'E4_Bvp 1680442028,67623 19,14136\r\n', 'E4_Bvp 1680442028,69185 18,61261\r\nE4_Bvp 1680442028,70748 18,84967\r\n', 'E4_Bvp 1680442028,7231 19,6001\r\n', 'E4_Bvp 1680442028,73873 20,34924\r\n', 'E4_Bvp 1680442028,75435 20,48132\r\n', 'E4_Bvp 1680442028,76998 19,51379\r\n', 'E4_Bvp 1680442028,78561 17,28156\r\n', 'E4_Bvp 1680442028,80123 14,00049\r\n', 'E4_Bvp 1680442028,81686 10,22882\r\n', 'E4_Bvp 1680442028,83248 6,667908\r\n', 'E4_Bvp 1680442028,84811 3,980774\r\n', 'E4_Bvp 1680442028,86373 2,527832\r\n', 'E4_Bvp 1680442028,87936 2,276855\r\n', 'E4_Bvp 1680442028,89499 2,756042\r\n', 'E4_Bvp 1680442028,91061 3,210693\r\n', 
    # 'E4_Bvp 1680442028,92624 2,876648\r\n', 'E4_Bvp 1680442028,94186 1,202393\r\n', 'E4_Bvp 1680442028,95749 -1,954712\r\n', 'E4_Bvp 1680442028,97311 -6,279053\r\n', 'E4_Bvp 1680442028,98874 -11,09271\r\n', 
    # 'E4_Bvp 1680442029,00437 -15,52991\r\n', 'E4_Gsr 1680442027,73 0,08067529\r\n', 'E4_Gsr 1680442027,98 0,0832364\r\nE4_Gsr 1680442028,23 0,08195585\r\n', 'E4_Gsr 1680442028,48 0,0832364\r\n', 'E4_Gsr 1680442028,73 0,0832364\r\n', 'E4_Gsr 1680442028,98 0,0832364\r\n', 'E4_Bvp 1680442029,01999 -18,76831\r\n', 'E4_Bvp 1680442029,03562 -20,34393\r\nE4_Bvp 1680442029,05124 -20,38129\r\n', 'E4_Bvp 1680442029,06687 -19,63263\r\n', 'E4_Bvp 1680442029,08249 -19,30249\r\n', 'E4_Bvp 1680442029,09812 -20,71851\r\n', 'E4_Bvp 1680442029,11375 -24,83002\r\n', 'E4_Bvp 1680442029,12937 -31,8396\r\n', 'E4_Bvp 1680442029,145 -41,0896\r\n', 'E4_Bvp 1680442029,16062 -51,1333\r\n', 'E4_Bvp 1680442029,17625 -60,12396\r\n', 'E4_Bvp 1680442029,19187 -66,22949\r\n', 'E4_Bvp 1680442029,2075 -68,0304\r\nE4_Bvp 1680442029,22313 -64,83942\r\n', 'E4_Bvp 1680442029,23875 -56,84741\r\n', 'E4_Bvp 1680442029,25438 -45,15454\r\n', 'E4_Bvp 1680442029,27 -31,54852\r\n', 'E4_Bvp 1680442029,28563 -18,07819\r\n', 'E4_Bvp 1680442029,30125 -6,531494\r\n', 'E4_Bvp 1680442029,31688 2,022156\r\n', 'E4_Bvp 1680442029,33251 7,461182\r\n', 'E4_Bvp 1680442029,34813 10,48157\r\n', 'E4_Hr 1680442023,65431 54,8546\r\n', 'E4_Ibi 1680442023,65431 1,093801\r\nE4_Bvp 1680442029,36376 12,16321\r\n', 'E4_Bvp 1680442029,37938 13,54291\r\n', 'E4_Bvp 1680442029,39501 15,21429\r\n', 'E4_Bvp 1680442029,41063 17,25928\r\n', 'E4_Bvp 1680442029,42626 19,40759\r\nE4_Bvp 1680442029,44189 21,289\r\n', 'E4_Bvp 1680442029,45751 22,63861\r\n', 'E4_Bvp 1680442029,47314 23,42334\r\n', 'E4_Bvp 1680442029,48876 23,79321\r\n', 'E4_Bvp 1680442029,50439 23,92487\r\n', 'E4_Bvp 1680442029,52001 23,91174\r\n', 'E4_Bvp 1680442029,53564 23,79108\r\n', 'E4_Bvp 1680442029,55127 23,62897\r\n', 'E4_Bvp 1680442029,56689 23,60065\r\n', 'E4_Bvp 1680442029,58252 24,0036\r\n', 'E4_Bvp 1680442029,59814 25,07147\r\n', 'E4_Bvp 1680442029,61377 26,771\r\n', 'E4_Bvp 1680442029,62939 28,71985\r\n', 'E4_Bvp 1680442029,64502 30,25751\r\n', 'E4_Bvp 1680442029,66065 30,75629\r\n', 'E4_Bvp 1680442029,67627 29,93719\r\n', 'E4_Bvp 1680442029,6919 28,01019\r\n', 'E4_Bvp 1680442029,70752 25,59662\r\n', 'E4_Bvp 1680442029,72315 23,39038\r\n', 'E4_Bvp 1680442029,73877 21,87573\r\n', 'E4_Bvp 1680442029,7544 21,02588\r\n', 'E4_Bvp 1680442029,77003 20,47162\r\n', 'E4_Bvp 1680442029,78565 19,78015\r\n', 'E4_Bvp 1680442029,80128 18,7113\r\n', 'E4_Bvp 1680442029,8169 17,42273\r\n', 'E4_Bvp 1680442029,83253 16,36548\r\n', 'E4_Bvp 1680442029,84815 16,03528\r\n', 'E4_Bvp 1680442029,86378 16,71814\r\n', 'E4_Bvp 1680442029,87941 18,40674\r\n', 'E4_Bvp 1680442029,89503 20,78082\r\n', 'E4_Bvp 1680442029,91066 23,38361\r\n', 'E4_Bvp 1680442029,92628 25,73895\r\n', 'E4_Bvp 1680442029,94191 27,51849\r\n', 'E4_Bvp 1680442029,95754 28,56287\r\n', 'E4_Bvp 1680442029,97316 28,85211\r\n', 'E4_Bvp 1680442029,98879 28,5307\r\n', 'E4_Bvp 1680442030,00441 27,8667\r\n', 'E4_Bvp 1680442030,02004 27,16815\r\n', 'E4_Bvp 1680442030,03566 26,67847\r\n', 'E4_Bvp 1680442030,05129 26,42834\r\n', 'E4_Bvp 1680442030,06692 26,15857\r\nE4_Bvp 1680442030,08254 25,34027\r\n', 'E4_Bvp 1680442030,09817 23,3103\r\n', 'E4_Bvp 1680442030,11379 19,48798\r\n', 'E4_Bvp 1680442030,12942 13,53955\r\n', 'E4_Bvp 1680442030,14504 5,518433\r\n', 'E4_Bvp 1680442030,16067 -4,075867\r\n', 'E4_Bvp 1680442030,1763 -14,27435\r\n', 'E4_Bvp 1680442030,19192 -23,77563\r\n', 'E4_Bvp 1680442030,20755 -31,18225\r\n', 'E4_Bvp 1680442030,22317 -35,34058\r\n', 'E4_Bvp 1680442030,2388 -35,716\r\n', 'E4_Bvp 1680442030,25442 -32,6037\r\n', 'E4_Bvp 1680442030,27005 -27,01813\r\n', 'E4_Bvp 1680442030,28568 -20,34424\r\n', 'E4_Bvp 1680442030,3013 -13,90161\r\n', 'E4_Bvp 1680442030,31693 -8,538452\r\n', 'E4_Bvp 1680442030,33255 -4,516479\r\n', 'E4_Bvp 1680442030,34818 -1,639587\r\n', 'E4_Bvp 1680442030,3638 0,4731445\r\n', 'E4_Bvp 1680442030,37943 2,12085\r\n', 'E4_Gsr 1680442029,23 0,07939473\r\n', 'E4_Gsr 1680442029,48 0,0832364\r\nE4_Gsr 1680442029,73 0,08067529\r\n', 'E4_Gsr 1680442029,98 0,08067529\r\n', 'E4_Gsr 1680442030,23 0,08451696\r\n', 'E4_Gsr 1680442030,48 0,08067529\r\n', 
    # 'E4_Bvp 1680442030,39506 3,331482\r\n', 'E4_Bvp 1680442030,41068 3,97821\r\n', 'E4_Hr 1680442024,70123 57,31078\r\n', 'E4_Ibi 1680442024,70123 1,046923\r\n', 'E4_Bvp 1680442030,42631 3,828857\r\n', 'E4_Bvp 1680442030,44193 2,742615\r\nE4_Bvp 1680442030,45756 0,8103027\r\n', 'E4_Bvp 1680442030,47318 -1,656189\r\n', 'E4_Bvp 1680442030,48881 -4,165039\r\n', 'E4_Bvp 1680442030,50444 -6,174377\r\n', 'E4_Bvp 1680442030,52006 -7,185669\r\n', 'E4_Bvp 1680442030,53569 -6,811279\r\n', 'E4_Bvp 1680442030,55131 -4,881531\r\n', 'E4_Bvp 1680442030,56694 -1,402466\r\n']

################3
# e4 = E4('127.0.0.1', 28000)

# start = time.time()
# delta = 0
# e4.E4_SS_connect()
# e4.start_subscriptions()
# while delta < 20:
#     arr = e4.recieve_data()
#     print(arr)
#     bvp = arr[1]
#     print(bvp[bvp.find(":"):])
#     delta = time.time() - start 
##############

# arr = ['Hr:68,56825', 'Bvp:-51,69904', 'Gsr:0,04481689']
# bvp = arr[1]
# print(bvp[bvp.find(":")+1:])


# e4.e4_stop()

# ['', 'Bvp:28,88359', 'Gsr:0,05634124']
# ['', 'Bvp:1,217896', 'Gsr:0,05506076']
# ['', 'Bvp:-365,4111', 'Gsr:0,05506076']
# ['', 'Bvp:62,82471', 'Gsr:0,04865834']
# ['', 'Bvp:48,9585', 'Gsr:0,04609737']
# ['', 'Bvp:-11,72839', 'Gsr:0,04609737']
# ['', 'Bvp:-49,37', 'Gsr:0,04865834']
# ['', 'Bvp:-45,36536', 'Gsr:0,04481689']
# ['', 'Bvp:20,1217', 'Gsr:0,04481689']
# ['', 'Bvp:17,96448', 'Gsr:0,04737785']
# ['', 'Bvp:40,36072', 'Gsr:0,04609737']
# ['', 'Bvp:6,785339', 'Gsr:0,04609737']
# ['', 'Bvp:-52,33167', 'Gsr:0,04609737']
# ['Hr:68,56825', 'Bvp:-51,69904', 'Gsr:0,04481689']
# ['Hr:67,3653', 'Bvp:43,99561', 'Gsr:0,04737785']
# ['Hr:63,99702', 'Bvp:43,13422', 'Gsr:0,04737785']
# ['Hr:63,99702', 'Bvp:50,02826', 'Gsr:0,04481689']
# ['Hr:66,20383', 'Bvp:50,46475', 'Gsr:0,04993882']
# ['Hr:61,93262', 'Bvp:27,19405', 'Gsr:0,04993882']

# e4 = E4('127.0.0.1', 28000)

# start = time.time()
# delta = 0
# e4.E4_SS_connect()
# e4.start_subscriptions()
# while delta < 20:
#     arr = e4.recieve_data()
#     # print(arr)
#     # bvp = arr[1]
#     # print(bvp[bvp.find(":"):])
#     delta = time.time() - start 