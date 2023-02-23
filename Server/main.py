
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


full_df = pd.DataFrame()
eeg_data_dict = {}
eye_data_dict = {}

#extension settings
settings = {
    "extension": True,
    "EEG": True,
    "E4": False
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
 
# yo 
def get_EEG_data():
    global eeg_data_dict
    while True:
        eeg_data_dict = get_EEG_data.get_EEG_data()

def get_eye_tracker_data():
    eye_tracker = EyeTracker(1)
    eye_tracker.setup()
    # eye_tracker.start_recording() 
    
    global eye_data_dict
    
    eye_tracker.start_recording(eye_data_dict)
    
    # while True:
    #     eye_tracker.store_to_cache(eye_tracker.eye_tracker.get_gaze_position())
    #     eye_data_dict = eye_tracker.get_recording()
        

def update_dataframe():
    global full_df
    global eye_data_dict
    global eeg_data_dict

    while True:
        time.sleep(1)
        full_data_dic = {}
        full_data_dic.update(eye_data_dict)
        full_data_dic.update(eeg_data_dict)
        
        full_df.append(full_data_dic)



if __name__ == "__main__":
    extensionCon_thread = threading.Thread(target=extension_connected, daemon=True)
    extensionCon_thread.start()

    #waiting for extension to connect to the server
    while extension_connected == False:
        time.sleep(1)
        print("waiting for connection")
    print("extension connected")
    
    if settings["EEG"] == True:
        #start thread/-s needed for EEG
        eeg_thread = threading.Thread(target=get_EEG_data, daemon=True)
        eeg_thread.start()
    
    if settings["Eye tracker"] == True:
        #start thread/-s needed for EEG
        eye_thread = threading.Thread(target=get_EEG_data, daemon=True)
        eye_thread.start()

        
    # once every second time values are stored                                  ####### ADDERA LOOP
    df_thread = threading.Thread(target=update_dataframe, daemon=True)
    df_thread.start()
    

