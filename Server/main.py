
## MEMES
# #(╯°□°)╯︵ ┻━┻ :^) ┬─┬ノ( º _ ºノ)
# (╯°Д°)╯︵/(.□ . \)
#HAHAHAHAHHA123
# ( ͡° ͜ʖ ͡°)
#
## THE VOICES
#Wake up
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

#  Local imports
from Hardware.EEG import EEG
from Hardware.Eyetracker.eyetracker import EyeTracker

from Hardware.E4 import E4_Object

# imports
import pandas as pd
import threading
import time
from datetime import datetime
import socket
import asyncio
import json

# FOR TESTING
import random

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages



# global variables
# socket settings
HOST_IP = "127.0.0.1" #lokala IPN, localhost
PORT = 6969 #lustigt. najs.
extension_connected = False
time_dict = {}
eeg_data_dict = {}
eye_data_dict = {}
e4_data_dict = {}
full_data_dict = {}
full_df = pd.DataFrame(dtype='object')
max_time = 500000

#extension settings
settings = {
    "extension": True,
    "EEG": False,
    "Eye tracker": False,
    "E4": False,
    "Garmin": False,
    "Save_path": 'D:/codez/EmoIDE_project/Server/Output',
    "Save_format": '.tsv'
    }

eeg_settings = {
    "client_id": "",
    "client_secret": ""
}

calibration_done = {
    "Eye tracker": False,
    "EEG": True,
    "Dataframe": True
    }


# start serverside with a tcp socket. AF - Address Family (IPv4). Sock_stream - type (TCP)
def setup_server():
    global tcp_socket
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((HOST_IP, PORT))
    tcp_socket.listen()
    print(f"SERVER: Hosting on IP:{HOST_IP} and listening on port:{PORT}")  

#handles the connection to the extension
def tcp_communication():
    global extension_connected
    conn, client = tcp_socket.accept()
    print(f"Connected to {client}")
    extension_connected = True
    start = time.time()
    delta = 0
    print(f"Connected to {client}")
    while delta <= max_time:
        delta = time.time() - start
        data_received = conn.recv(1024).decode('utf-8')
        if not data_received.strip():
            break
        json_data = json.loads(data_received)
        recived_msg = json_data["function"]
        # mest för att testa så klienten och servern kan kommunicera
        
        if recived_msg == "ping":
            print("ping")
            data = {
                "function": "ping",
                }
            data_json = json.dumps(data)
            conn.sendall(data_json.encode('utf-8'))
            print("Received a ping from the client & responded with pong.")

        elif recived_msg == "getPulse":
            print("hey")
            pulse = e4_data_dict["Pulse"]
            data = {
                "function": "getCurrentPulse",
                "data": random.randint(80, 120)
                }
            data_json = json.dumps(data)
            conn.sendall(data_json.encode('utf-8'))



        elif recived_msg == "getEEG":
            eeg = eeg_data_dict
            #use real eeg data later
            eeg_data = {
                "function": "getEEGData",
                "data": {
                    "Engagement":random.random(),
                    "Excitement":random.random(),
                    "Long term excitement":random.random(),
                    "Stress/Frustration":random.random(),
                    "Relaxation":random.random(),
                    "Interest/Affinity":random.random(),
                    "Focus":random.random()
                }

            }
            eeg_data_json = json.dumps(eeg_data)
            
            conn.sendall(eeg_data_json.encode('utf-8'))


        # new save location     # msg: "set_save_path: [SPACE] root/path/location"
        elif "set_save_path:" in recived_msg:
            path_pos = recived_msg.find("set_save_path:")
            picked_path = recived_msg[path_pos+5:]             # hämtar alla tecken efter "path:"
            settings["Save_path"] = picked_path
        
        # new format type for saved file
        elif "set_save_format:" in recived_msg:
            format_pos = recived_msg.find("set_save_format:")
            picked_format = recived_msg[format_pos+7:format_pos+11]             # hämtar 4 tecken efter "format:"       -> ex. '.csv'       FIXA FÖR .XLSX som är 5 tecken. Pinga endast ".xls"
            settings["Save_format"] = picked_format
            
    conn.close()

async def import_EEG_data():
    global eeg_data_dict
    global calibration_done

    cortex_api = EEG.EEG()
    await cortex_api.connect()
    await cortex_api.setup()
    
    #wait for first message
    #await cortex_api.get_eeg_data()

    calibration_done["EEG"] = True

    all_done = True
    while not all_done:
        if all(sensor_calibration == True for sensor_calibration in calibration_done.values()):
            all_done = True
    
    start = time.time()
    while time.time() - start < 40:
        time.sleep(1)
        eeg_data_dict = await cortex_api.get_eeg_data()

    await cortex_api.end_session()

def start_eeg():
    asyncio.run(import_EEG_data())


# -------------- EYE TRACKER -------------- #

def get_eye_tracker_data():
    global calibration_done
    global eye_data_dict

    eye_tracker = EyeTracker(1)
    eye_tracker.setup()
    print("setup done")
    calibration_done["Eye tracker"] = True

    all_done = False
    while not all_done:
        if all(sensor_calibration == True for sensor_calibration in calibration_done.values()):
            all_done = True
    
    eye_tracker.start_recording(eye_data_dict)
    eye_tracker.stop()

# GETTERS

def get_eye_coordinates_in_time_range(start_time, end_time):
    range_mask = (full_df["Time"] > start_time) & (full_df["Time"] <= end_time)
    return full_df.loc[range_mask]



# ---------------E4 DATA TRACKER---------------- #
def get_e4_data():
    global e4_data_dict

    e4 = E4_Object.E4('127.0.0.1', 28000)

    e4.E4_SS_connect()

    e4.start_subscriptions()

    start = time.time()
    while time.time() - start < 40:
        e4.recieve_data(e4_data_dict)
    # add data from function in E4/E4SS_client.py
    e4.e4_stop()


def init_df():
    global time_dict
    global eeg_data_dict
    global eeg_data_dict
    global e4_data_dict
    global full_data_dict
    global full_df

    full_df = pd.DataFrame(dtype='object')

    time_dict = {
        "time":0
    }

    eye_data_dict = {
    "x":0,
    "y":0,
    "Explorer": 0,
    "Terminal": 0,
    "Code": 0
    }

    eeg_data_dict = {
        "Engagement":0,
        "Excitement":0,
        "Long term excitement":0,
        "Stress/Frustration":0,
        "Relaxation":0,
        "Interest/Affinity":0,
        "Focus":0
        }
    
    e4_data_dict = {
        "Pulse":0
    }

    full_data_dict.update(time_dict)
    full_data_dict.update(eye_data_dict)
    full_data_dict.update(eeg_data_dict)
    full_data_dict.update(e4_data_dict)                           ####################### Lägg till när e4 redo

    full_df = full_df.append(full_data_dict, ignore_index = True)


    
def update_dataframe():
    global full_df
    calibration_done["Dataframe"] = True
    all_done = True
    while not all_done:
        if all(sensor_calibration == True for sensor_calibration in calibration_done.values()):
            all_done = True

    start = time.time()
    delta = 0
    while delta <= max_time:
        delta = time.time() - start
        full_data_dic = {}
        time.sleep(1)

        # Clear terminal
        #os.system('cls' if os.name == 'nt' else 'clear')

        # time
        # time_dict["time"] = time.localtime()

        # time_dict["time"] = time.gmtime()
        # This gives the format - dd/mm/yy-HH:MM:SS
        time_dict["time"] = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

        # 
        full_data_dic.update(time_dict)

        # Eye tracker
        # print(f"eyetracker dict:{eye_data_dict}\n")
        # print(eye_data_dict)
        full_data_dic.update(eye_data_dict)
        
        # Eeg
        # print(f"eeg dict:{eeg_data_dict}\n")
        full_data_dic.update(eeg_data_dict)

        full_data_dic.update(e4_data_dict)
        
        # dataframe
        # print(f"dict: {full_data_dic}\n")
        #delta_decimaler = (delta - int(delta))
        #time.sleep(delta_decimaler)
        # time.sleep(1 - (1-((time.time() - start) - delta)))
        full_df = full_df.append(full_data_dic,ignore_index=True, sort=False)

        #print(f"{full_df}\n--------------------------------")


def save_df(df, path, save_as_ext = '.csv'):
    filename = 'output_data'    # get last part of path

    # checks if path exists on comupter
    if not (os.path.exists(path)):
        print("Filepath does not exist")
        return 0

    if save_as_ext == '.pdf':
        filename = filename + save_as_ext

        #Skapar ett table från dataframe
        fig, ax =plt.subplots(figsize=(12,4))
        ax.axis('tight')
        ax.axis('off') 
        # osäker på vad denna gör men fungerar inte utan
        the_table = ax.table(cellText=df.values,colLabels=df.columns,loc='center')

        #Skapar ett tomt pdf dokument och sparar sedan figuren i det
        pp = PdfPages(filename = str(path + "/" + filename))
        pp.savefig(fig, bbox_inches='tight')
        pp.close()
        
    elif save_as_ext == '.tsv':
        filename = filename + save_as_ext
        df.to_csv(str(path + "/" + filename), sep="\t")
    
    elif save_as_ext == '.html':
        filename = filename + save_as_ext
        html = df.to_html()
  
        # write html to file
        text_file = open(str(path + "/" + filename), "w")
        text_file.write(html)
        text_file.close()

    elif save_as_ext == '.ods':
        filename = filename + save_as_ext
        with pd.ExcelWriter(str(path + "/" + filename)) as writer:          # ERROR "no module odf"
            df.to_excel(writer) 

    elif save_as_ext == '.xlsx':
        filename = filename + save_as_ext
        df.to_excel(str(path + "/" + filename))
    else:
        filename = filename + '.csv'
        df.to_csv(str(path + "/" + filename))


#### TESTFUNKTION
def TEST_create_mock_dataframe(test_time):    
    mock_full_df = pd.DataFrame()

    # Init dataframe
    # full_data_dict = {}
    # eye_data_dict = {}
    # eeg_data_dict = {}

    time_dict = {
        "time":"time0"
    }

    eye_data_dict = {
    "x":0,
    "y":0
    }

    eeg_data_dict = {
        "Engagement":0,
        "Excitement":0,
        "Long term excitement":0,
        "Stress/Frustration":0,
        "Relaxation":0,
        "Interest/Affinity":0,
        "Focus":0
        }

    full_data_dict.update(time_dict)
    full_data_dict.update(eye_data_dict)
    full_data_dict.update(eeg_data_dict)

    mock_full_df = mock_full_df.append(full_data_dict, ignore_index = True)

    start = time.time()
    while time.time() - start < test_time:
        time.sleep(1)

        rand_x = random.randint(0,10)
        rand_y = random.randint(0,10)
        
        rand_Engagment = random.randint(0,10)
        rand_Excitement = random.randint(0,10)
        rand_Long_Excitement = random.randint(0,10)
        rand_Frustration = random.randint(0,10)
        rand_Relaxation = random.randint(0,10)
        rand_Interest = random.randint(0,10)
        rand_Focus = random.randint(0,10)
        
        eye_data_dict["x"] = rand_x
        eye_data_dict["y"] = rand_y
        
        eeg_data_dict["Engagement"] = rand_Engagment
        eeg_data_dict["Excitement"] = rand_Excitement
        eeg_data_dict["Long term excitement"] = rand_Long_Excitement
        eeg_data_dict["Focus"] = rand_Focus
        eeg_data_dict["Interest/Affinity"] = rand_Interest
        eeg_data_dict["Relaxation"] = rand_Relaxation
        eeg_data_dict["Stress/Frustration"] = rand_Frustration

        full_data_dict.update(time_dict)
        full_data_dict.update(eye_data_dict)
        full_data_dict.update(eeg_data_dict)

        mock_full_df = mock_full_df.append(full_data_dict, ignore_index = True)

        # Print in terminal
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{mock_full_df}\n--------------------------------")

    return mock_full_df

def TEST_full_mock(path, format, test_time):
    df = TEST_create_mock_dataframe(test_time=10)
    save_df(df, path, format)                ################# LÄGG TILL EGEN PATH

    exit()

def start_threads():
    threads = []
    
    print("Server thread starts")
    com_thread = threading.Thread(target=tcp_communication, daemon=True)
    com_thread.start()
    #threads.append(com_thread)

    if settings["EEG"] == True:
        #start thread/-s needed for EEG
        print("EEG thread starts")
        eeg_thread = threading.Thread(target=start_eeg)
        eeg_thread.start()
        threads.append(eeg_thread)
    
    if settings["Eye tracker"] == True:
        #start thread/-s needed for Eye tracker
        print("Eye thread starts")
        eye_thread = threading.Thread(target=get_eye_tracker_data) # ALT. threading.Thread(target=get_eye_tracker_data, daemon=True)
        eye_thread.start()
        threads.append(eye_thread)
    
    if settings["E4"] == True:
         #start thread/-s needed for Empatica E4
        print("E4 thread starts")
        e4_thread = threading.Thread(target=get_e4_data) # ALT. threading.Thread(target=get_eye_tracker_data, daemon=True)
        e4_thread.start()
        threads.append(e4_thread)


    print("Dataframe thread starts")
    #df_thread = threading.Thread(target=update_dataframe, daemon=True)
    #df_thread.start()
    #threads.append(df_thread)

    return threads

def join_threads(threads):
    print(threads)
    for t in threads:
        print(f"----------  Joining {str(t)}  --------------")
        t.join()
        print(f"{str(t)} is now closed")

if __name__ == "__main__":
    # full_mock_test("PATH", '.csv', 11)          ################ Startar och avslutar en dataframe med fake-värden test

    # # Call this when stressed so the date and time match up on screenshot and stressed moment
    # dashboard.capture_screen()
    # # At end of session, or when you want to create dashboard call this, or maybe call it in the begining and have functions that updates it from here (or something)
    # dashboard.create_dashboard()


    # initiate global empty dataframe
    init_df()

    # start localy hosted server
    setup_server()

    # start all available hardware threads and return array of activated threads
    threads = start_threads()

    # stop main thread until everything is finished         ############# Remake to a bool check so that it isn't time relyable
    time.sleep(max_time+4)

    # closing all the active threads
    join_threads(threads)

    # Save dataframe to a path and with specified format
    save_format = settings["Save_format"]
    save_path = settings["Save_path"]
    save_df(full_df, save_path, save_format)
    
    exit()

