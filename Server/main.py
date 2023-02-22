import pandas as pd
import threading
import time
import datetime
import socket

HOST = "127.0.0.1"
PORT = 6969
extension_connected = False

eeg_data = {
    "timedate": [datetime.datetime.now()],
    "eeg_beta": ["14"],
    "eeg_alpha": ["8"],
    "eeg_theta": ["5"]
    }


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

def analyze_EEG():
    print("analyzing EEG data.")
    while True:
        df = pd.DataFrame(eeg_data)
        print(df.tail(1))
        time.sleep(1)

def eeg_connection():
    #connect to EEG & read data
    while True:
        time.sleep(2)
        print("reading EEG")
        
def empaticaE4_connection():
    #connect to E4 watch & read data
    while True:
        time.sleep(2)
        print("reading E4")

        
def eyetracker_connection():
    #connect to eyetracker watch & read data
    while True:
        time.sleep(2)
        print("reading eyetracker")
        

if __name__ == "__main__":
    
    extensionCon_thread = threading.Thread(target=extension_connected, daemon=True)
    extensionCon_thread.start()

    #waiting for extension to connect to the server
    while extension_connected == False:
        time.sleep(1)
        print("waiting for connection")
    print("extension connected")
    
    
    
    if settings["EEG"] == True:
        EEG_thread = threading.Thread(target=eeg_connection, daemon=True)
        analyzeEEG = threading.Thread(target=analyze_EEG, daemon=True)
        EEG_thread.start()
        analyzeEEG.start()
        
    
