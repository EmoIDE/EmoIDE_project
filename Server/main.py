
## MEMES
# #(╯°□°)╯︵ ┻━┻ :^) ┬─┬ノ( º _ ºノ)
# (╯°Д°)╯︵/(.□ . \)
#HAHAHAHAHHA123
# ( ͡° ͜ʖ ͡°)
#
## THE VOICES
#Wake up
#  Local imports
from Hardware.EEG import eeg
from Hardware.Eyetracker.eyetracker import EyeTracker

# imports
import os
import pandas as pd
import threading
import time
import datetime
import socket

# FOR TESTING
import random

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


HOST = "127.0.0.1"
PORT = 6969 #lustigt. najs.
extension_connected = False

eeg_data_dict = {}


eeg_data_dict = {}
eye_data_dict = {}

full_data_dict = {}

full_df = pd.DataFrame()

#extension settings
settings = {
    "extension": False,
    "Server connect": False,
    "EEG": False,
    "Eye tracker": False,
    "E4": False,
    "Garmin": False
    }

calibration_done = {
    "Eye tracker": False,
    "EEG": False,
    "Dataframe": False
    }



#handles the connection to the extension
def extension_connection():
    global extension_connected
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    print(f"Connected by {addr}")
    extension_connected = True
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
 
#
def import_EEG_data():
    global eeg_data_dict
    global calibration_done
    
    calibration_done["EEG"] = True

    all_done = False
    while not all_done:
        if all(sensor_calibration == True for sensor_calibration in calibration_done.values()):
            all_done = True
    
    start = time.time()
    while time.time() - start < 40:
        time.sleep(1)
        eeg_data_dict = eeg.get_EEG_data()

        #print(f"In get_EEG_data() dict is:{eeg_data_dict}")

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
    
    # while True:
    #     eye_tracker.store_to_cache(eye_tracker.eye_tracker.get_gaze_position())
    #     eye_data_dict = eye_tracker.get_recording()
        

def init_df():
    global full_df
    global full_data_dict
    global eye_data_dict
    global eeg_data_dict

    time = {
        "time":0
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

    full_data_dict.update(time)
    full_data_dict.update(eye_data_dict)
    full_data_dict.update(eeg_data_dict)

    full_df = full_df.append(full_data_dict, ignore_index = True)



def update_dataframe():
    global full_df
    global eye_data_dict
    global eeg_data_dict

    calibration_done["Dataframe"] = True

    all_done = False
    while not all_done:
        if all(sensor_calibration == True for sensor_calibration in calibration_done.values()):
            all_done = True



    start = time.time()
    while time.time() - start < 35:
        full_data_dic = {}
        time.sleep(1)

        # Clear terminal
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Eye tracker
        # print(f"eyetracker dict:{eye_data_dict}\n")
        full_data_dic.update(eye_data_dict)
        
        # Eeg
        # print(f"eeg dict:{eeg_data_dict}\n")
        full_data_dic.update(eeg_data_dict)
        
        # dataframe
        # print(f"dict: {full_data_dic}\n")
        full_df = full_df.append(full_data_dic,ignore_index=True, sort=False)

        print(f"{full_df}\n--------------------------------")


def save_df(df, path, save_as_ext):
    filename = 'output_data'    # get last part of path

    if save_as_ext == '.pdf':
        filename = filename + save_as_ext

        #Skapar ett table från dataframe
        fig, ax =plt.subplots(figsize=(12,4))
        ax.axis('tight')
        ax.axis('off') 
        # osäker på vad denna gör:
        the_table = ax.table(cellText=df.values,colLabels=df.columns,loc='center')

        #Skapar ett tomt pdf dokument och sparar sedan figuren i det
        pp = PdfPages(filename = str(path + "/" + filename))
        pp.savefig(fig, bbox_inches='tight')
        pp.close()
        
    elif save_as_ext == '.tsv':
        filename = filename + save_as_ext
        df.to_csv(str(path + "/" + filename), sep="\t")
    
# GER OK OUTPUT -> dock inte snygg
    elif save_as_ext == '.html':
        filename = filename + save_as_ext
        html = df.to_html()
  
        # write html to file
        text_file = open(str(path + "/" + filename), "w")
        text_file.write(html)
        text_file.close()

# FUNKAR INTE
    elif save_as_ext == '.ods':
        filename = filename + save_as_ext

## FUNKAR INTE
    elif save_as_ext == '.xlsx':
        filename = filename + save_as_ext
        # to excel file
        """ från geeks4geeks
        # saving xlsx file
        GFG = pd.ExcelWriter('Names.xlsx')
        df_new.to_excel(GFG, index=False)
        GFG.save()
        """
        excel_file = pd.ExcelWriter(str(path + "/" + filename))
        df.to_excel(excel_file, index=False)
        df.save()
    
    else:
        filename = filename + '.csv'
        df.to_csv(str(path + "/" + filename))


#### TESTFUNKTION
def TEST_create_mock_dataframe():
    mock_df = pd.DataFrame()

    mock_eye_dict = {
    "x":0,
    "y":0
    }

    start = time.time()
    while time.time() - start < 11:
        time.sleep(1)

        rand_x = random.randint(0,10)
        rand_y = random.randint(0,10)

        mock_eye_dict = {
            "x":rand_x,
            "y":rand_y
        }
        mock_df = mock_df.append(mock_eye_dict, ignore_index = True, sort=False)

        # Print in terminal
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{mock_df}\n--------------------------------")

    return mock_df


if __name__ == "__main__":
    df = TEST_create_mock_dataframe()
    save_df(df, 'PATH', '.html')
    
    
    exit()  # (!) EXIT FOR TESTING




    init_df()
    extensionCon_thread = threading.Thread(target=extension_connected, daemon=True)
    extensionCon_thread.start()

    # waiting for extension to connect to the server
    if settings["Server connect"] == True:
        while extension_connected == False:
            time.sleep(1)
            print("waiting for connection")
        print("extension connected")

    if settings["EEG"] == True:
        #start thread/-s needed for EEG
        print("EEG thread starts")
        eeg_thread = threading.Thread(target=import_EEG_data)
        eeg_thread.start()
    
    if settings["Eye tracker"] == True:
        #start thread/-s needed for Eye tracker
        print("Eye thread starts")
        eye_thread = threading.Thread(target=get_eye_tracker_data) # ALT. threading.Thread(target=get_eye_tracker_data, daemon=True)
        eye_thread.start()

    
    # once every second time values are stored                                  ####### ADDERA LOOP
    df_thread = threading.Thread(target=update_dataframe)
    # df_thread = threading.Thread(target=update_dataframe, daemon=True)
    df_thread.start()
    print("Dataframe thread starts")

    print("--------------- WAITING FOR EYE THREAD TO JOIN --------------- ")
    eye_thread.join()
    print("EYE Thread Done...")

    print("--------------- WAITING FOR DF THREAD TO JOIN --------------- ")
    df_thread.join()
    print("DF Thread Done...")

    save_df(full_df, "C:/Users/sebastian.johanss11/Desktop/Python grejer/Faktisk EmoIDE/EmoIDE_project-1/Server/Data.csv")

    print("--------------- WAITING FOR EEG THREAD TO JOIN --------------- ")
    eeg_thread.join()
    print("EEG Thread Done...")

    exit()
    # print("Before joining DF Thread: ")
    # eeg_thread.join()
    # print("EEG Thread Done...")

