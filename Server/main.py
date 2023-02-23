
## MEMES
# #(╯°□°)╯︵ ┻━┻ :^) ┬─┬ノ( º _ ºノ)
# (╯°Д°)╯︵/(.□ . \)
#HAHAHAHAHHA123
# ( ͡° ͜ʖ ͡°)
#
## THE VOICES
#Wake up
#  Local imports
from Hardware.EEG import get_EEG_data
from Hardware.Eyetracker.eyetracker import EyeTracker

# imports
import pandas as pd
import threading
import time
import datetime
import socket


HOST = "127.0.0.1"
PORT = 6969 #lustigt. najs.
extension_connected = False

eeg_data_dict = {}


eeg_data_dict = {}
eye_data_dict = {}

full_data_dict = {}

full_df = pd.DataFrame()

eye_calibration_done = False

#extension settings
settings = {
    "extension": False,
    "Server connect": False,
    "EEG": False,
    "Eye tracker": True,
    "E4": False,
    "Garmin": False
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
def get_EEG_data():
    global eeg_data_dict
    while True:
        eeg_data_dict = get_EEG_data.get_EEG_data()

def get_eye_tracker_data():
    global eye_calibration_done
    eye_tracker = EyeTracker(1)
    eye_tracker.setup()
    eye_calibration_done = True
    print("setup done")
    # eye_tracker.start_recording() 
    
    global eye_data_dict
    
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

    full_data_dict.update(eye_data_dict)
    full_data_dict.update(eeg_data_dict)

    full_df = full_df.append(full_data_dict, ignore_index = True)



def update_dataframe():
    global full_df
    global eye_data_dict
    global eeg_data_dict
    global eye_calibration_done

    print("Starting df update loop")
    start = time.time()
    while time.time() - start < 100:
        full_data_dic = {}
        time.sleep(1)
        if eye_calibration_done:
            # Eye tracker
            print(f"eyetracker dict:{eye_data_dict}\n")
            full_data_dic.update(eye_data_dict)
            
            # Eeg
            print(f"eeg dict:{eeg_data_dict}\n")
            full_data_dic.update(eeg_data_dict)
            
            # dataframe
            print(f"dict: {full_data_dic}\n")
            full_df = full_df.append(full_data_dic,ignore_index=True, sort=False)

            print(f"{full_df}\n--------------------------------")


def save_df(df, path):
    df.to_csv(path)


if __name__ == "__main__":
    init_df()
    extensionCon_thread = threading.Thread(target=extension_connected, daemon=True)
    extensionCon_thread.start()

    #waiting for extension to connect to the server
    if settings["Server connect"] == True:
        while extension_connected == False:
            time.sleep(1)
            print("waiting for connection")
        print("extension connected")

    if settings["EEG"] == True:
        #start thread/-s needed for EEG
        eeg_thread = threading.Thread(target=get_EEG_data)
        # eeg_thread = threading.Thread(target=get_EEG_data, daemon=True)
    
    if settings["Eye tracker"] == True:
        #start thread/-s needed for EEG
        eye_thread = threading.Thread(target=get_eye_tracker_data)
        # eye_thread = threading.Thread(target=get_eye_tracker_data, daemon=True)
        eye_thread.start()

    # once every second time values are stored                                  ####### ADDERA LOOP
    df_thread = threading.Thread(target=update_dataframe)
    # df_thread = threading.Thread(target=update_dataframe, daemon=True)
    df_thread.start()

    print("--------------- WAITING FOR EYE THREAD TO JOIN --------------- ")
    eye_thread.join()
    print("EYE Thread Done...")

    print("--------------- WAITING FOR DF THREAD TO JOIN --------------- ")
    df_thread.join()
    print("DF Thread Done...")

    save_df(full_df, "C:/Users/sebastian.johanss11/Desktop/Python grejer/Faktisk EmoIDE/EmoIDE_project-1/Server/Data.csv")

    # print("--------------- WAITING FOR EEG THREAD TO JOIN --------------- ")
    # eeg_thread.join()
    # print("EEG Thread Done...")

    exit()
    # print("Before joining DF Thread: ")
    # eeg_thread.join()
    # print("EEG Thread Done...")

