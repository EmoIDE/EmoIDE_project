
## MEMES
# #(╯°□°)╯︵ ┻━┻ :^) ┬─┬ノ( º _ ºノ)
# (╯°Д°)╯︵/(.□ . \)
#HAHAHAHAHHA123
# ( ͡° ͜ʖ ͡°)
## THE VOICES
#Wake up
import os
import sys
import jinja2

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

#  Local imports
from Hardware.EEG import EEG
from Hardware.Eyetracker.eyetracker import EyeTracker
from Hardware.E4 import E4_client
from ML import Pop_up
import Dashboard.dashboard as dashboard

# imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import threading
import time
import socket
import asyncio
import json
import datetime
import pickle
import random
from matplotlib.backends.backend_pdf import PdfPages

from sklearn.preprocessing import scale
import joblib


format = "%d-%m-%YT%H-%M-%S"


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
max_time = 10
bad_path = os.path.dirname(os.path.realpath(__file__)) + "/settings.json"  # f'{os.path.dirname(os.path.abspath(__file__))}/settings.json'
SETTINGS_PATH = bad_path.replace("\\", "/")  # f'{os.path.dirname(os.path.abspath(__file__))}/settings.json'

#extension settings
settings_dict = {
    }

training_dict = {
}

eeg_settings = {
    "client_id": "",
    "client_secret": ""
}

calibration_done = {
    "Eye tracker": False,
    "EEG": False,
    "E4": False,
    "Dataframe": True
    }

# ------------------------------------------ Server ------------------------------------------ #
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
    tcp_socket.settimeout(10)

    # loop and try to connect to extention
    extension_connected = False
    connect_test = 0
    while not extension_connected and connect_test < 2:
        try:
            connect_test += 1
            conn, client = tcp_socket.accept()
            extension_connected = True
        except:
            print("not connected")
    try:
        print(f"Connected to {client}")
    except:
        print("Failed to connect to extension")
        return 0
    

    # Commands
    start = time.time()
    delta = 0
    while delta <= max_time:
        delta = time.time() - start
        try:
            data_received = conn.recv(1024).decode('utf-8')
        except:
            print("no message")
        if not data_received.strip():
            break
        json_data = json.loads(data_received)
        recived_msg = json_data["function"]
        # mest för att testa så klienten och servern kan kommunicera
        

        print(recived_msg)
        if recived_msg == "settings_update":
            read_settings(SETTINGS_PATH)
            print(settings_dict)

        if recived_msg == "getEmotion":
            conn.sendall(json.dumps(prediction_dict).encode('utf-8'))
            print("changed SAM on extension")

        if recived_msg == "ping":
            print("ping")
            data = {
                "function": "ping",
                }
            data_json = json.dumps(data)
            conn.sendall(data_json.encode('utf-8'))
            print("Received a ping from the client & responded with pong.")

        elif recived_msg == "getPulse":
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
            picked_path = recived_msg[path_pos+11:]             # hämtar alla tecken efter "set_save_path:"
            settings_dict["Save_path"] = picked_path
        
        # new format type for saved file
        elif "set_save_format:" in recived_msg:
            format_pos = recived_msg.find("set_save_format:")
            picked_format = recived_msg[format_pos+7:format_pos+11]             # hämtar 4 tecken efter "format:"       -> ex. '.csv'       FIXA FÖR .XLSX som är 5 tecken. Pinga endast ".xls"
            settings_dict["Save_format"] = picked_format
            
    conn.close()


# ------------------------------------------ EEG ------------------------------------------ #
async def import_EEG_data():
    global eeg_data_dict
    global calibration_done
    global max_time

    cortex_api = EEG.EEG()
    await cortex_api.connect()
    await cortex_api.setup()
    
    #wait for first message
    #await cortex_api.get_eeg_data()

    calibration_done["EEG"] = True

    all_done = False
    while not all_done:
        if all(sensor_calibration == True for sensor_calibration in calibration_done.values()):
            all_done = True
    
    start = time.time()
    while time.time() - start < max_time:
        time.sleep(1)
        eeg_data_dict = await cortex_api.get_eeg_data()

    await cortex_api.end_session()


def start_eeg():
    asyncio.run(import_EEG_data())


# ------------------------------------------ EYE TRACKER ------------------------------------------ #
def get_eye_tracker_data():
    global calibration_done
    global eye_data_dict
    global full_df

    eye_tracker = EyeTracker(1, max_time)
    eye_tracker.setup()
    print("setup done")
    calibration_done["Eye tracker"] = True

    all_done = False
    while not all_done:
        if all(sensor_calibration == True for sensor_calibration in calibration_done.values()):
            all_done = True

    eye_tracker.start_recording(eye_data_dict)
    eye_tracker.stop()


# ------------------------------------------ E4 DATA TRACKER ------------------------------------------ #
def get_e4_data():
    #global calibration_done
    global e4_data_dict

    # init object
    e4 = E4_client.E4('127.0.0.1', 28000)
    # connect and start getting Bvp, Gsr and Hr data
    e4.E4_SS_connect()
    e4.start_subscriptions()

    calibration_done["E4"] = True
    all_done = False                                                                     ######################
    # while not all_done:
    #     if all(sensor_calibration == True for sensor_calibration in calibration_done.values()):
    #         all_done = True
    print("e4 start recording")

    start = time.time()
    while time.time() - start < max_time:
        data = e4.recieve_data()
        hr = data[0]
        bvp = data[1]
        gsr = data[2]

        # Om de nya värdena är tomma, ersätt inte till dataframen.
        if not hr == "":
            hr_string = hr[hr.find(":")+1:]
            if float(hr_string.replace(",", ".")) > 20:
                e4_data_dict["Pulse"] = hr_string            ##### EJ TESTAT
        if not bvp == "":
            e4_data_dict["Bvp"] = bvp[bvp.find(":")+1:]
        if not gsr == "":
            e4_data_dict["Gsr"] = gsr[gsr.find(":")+1:]
        
    # e4.e4_stop()                      # Printar resterande grejer i bufferten. Ta bort eller få den att sluta printa. Raden behövs tekniskt sätt inte.


# ------------------------------------------ DataFrame ------------------------------------------ #
def init_df():
    global time_dict
    global eye_data_dict
    global eeg_data_dict
    global e4_data_dict
    global prediction_dict
    global full_data_dict
    global full_df
    global training_dict

    full_df = pd.DataFrame(dtype='object')

    time_dict = {
        "time":datetime.datetime.now().strftime("%d-%m-%YT%H-%M-%S")
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
        "Pulse":0,
        "Bvp":0,
        "Gsr": 0
    }

    prediction_dict = {
        "Valence":0,
        "Arousal":0
    }

    # if settings_dict["Training"] == True:
    #     training_dict = {
    #         "Name":"Jane Doe",
    #         "Age": None,
    #         "Initial pulse": None,
    #         "Arousal": None,
    #         "Valence": None,
    #         "Gender" : None,
    #         "Stress": 0
    #     }
        
    #     training_dict["Name"] = Pop_up.get_name() #samlar ursprungliga värden
    #     training_dict["Age"] = Pop_up.get_age()
    #     training_dict["Gender"] = Pop_up.get_gender()
    #     training_dict["Arousal"] = Pop_up.test_arousal() + 1
    #     training_dict["Valence"] = Pop_up.test_valence() + 1
    #     training_dict["Stress"] = Pop_up.get_stress()
    #     full_data_dict.update(training_dict)

    full_data_dict.update(time_dict)
    full_data_dict.update(eye_data_dict)
    full_data_dict.update(eeg_data_dict)
    full_data_dict.update(e4_data_dict)
    full_data_dict.update(prediction_dict)

    full_df = full_df.append(full_data_dict, ignore_index = True)

    
def update_dataframe(mock = False):
    global full_df
    global max_time
    calibration_done["Dataframe"] = True
    all_done = False                                                                     ######################
    while not all_done:
        if all(sensor_calibration == True for sensor_calibration in calibration_done.values()):
            all_done = True

    data_collection_timer = time.time()

    start = time.time()
    delta = 0
    while delta <= max_time:
        delta = time.time() - start
        full_data_dict = {}
        time.sleep(1)

        if mock == True:
            mock_all_dicts()

        # Clear terminal
        #os.system('cls' if os.name == 'nt' else 'clear')                        ############################

        # time
        # time_dict["time"] = time.localtime()

        # time_dict["time"] = time.gmtime()
        # This gives the format - dd/mm/yy-HH:MM:SS
        time_dict["time"] = datetime.datetime.now().strftime("%d-%m-%YT%H-%M-%S")

        # time
        full_data_dict.update(time_dict)

        # Eye tracker
        full_data_dict.update(eye_data_dict)
        
        # Eeg
        full_data_dict.update(eeg_data_dict)

        # E4
        full_data_dict.update(e4_data_dict)

        # Prediction
        full_data_dict.update(prediction_dict)
        
        # Training
        training_time = 300

        # if settings_dict["Training"] == True:
        #     if e4_data_dict["Pulse"] != 0 and training_dict["Initial pulse"] == None:
        #         training_dict["Initial pulse"] = e4_data_dict["Pulse"]
        #     if time.time() - data_collection_timer > training_time:
        #         training_dict["Arousal"] = Pop_up.test_arousal() + 1
        #         training_dict["Valence"] = Pop_up.test_valence() + 1
        #         training_dict["Stress"] = Pop_up.get_stress()

        #         data_collection_timer = time.time()
        #     full_data_dict.update(training_dict)
        #     training_dict["Valence"] = None
        #     training_dict["Arousal"] = None
        #     training_dict["Stress"] = 0

        try:
            predict_series()
        except:
            print("prediction failed - prediction_dict not updated")
        # dataframe
        full_df = full_df.append(full_data_dict,ignore_index=True, sort=False)

        print(f"{full_df}\n--------------------------------")                                     ###########################


def mock_all_dicts():
    global eye_data_dict
    global eeg_data_dict
    global e4_data_dict

    eye_data_dict["x"] = random.random()
    eye_data_dict["y"] = random.random()
    eeg_data_dict = {
            "Engagement":random.random(),
            "Excitement":random.random(),
            "Long term excitement":random.random(),
            "Stress/Frustration":random.random(),
            "Relaxation":random.random(),
            "Interest/Affinity":random.random(),
            "Focus":random.random()
    }

    e4_data_dict["Bvp"] = random.randrange(-100, 100)
    e4_data_dict["Gsr"] = random.randrange(1, 3) / 10
    e4_data_dict["Pulse"] = random.randrange(60, 100)

# ------------------------------------------ AI ------------------------------------------ #
def predict_series():
    global eeg_predict_values
    full_data_dict["Gender"] = settings_dict["Gender"]
    full_data_dict["Age"] = settings_dict["Age"]
    eeg_predict_values = pd.Series(full_data_dict)

    drop_list = ["time", "x", "y", "Explorer", "Terminal", "Code", "Pulse", "Bvp", "Gsr", "Valence", "Arousal"]
    eeg_predict_values.drop(drop_list, inplace=True)
    
    predict_frame = pd.DataFrame(eeg_predict_values)
    predict_frame= predict_frame.transpose()

    predict_frame = pd.get_dummies(predict_frame, columns=["Gender"])

    # svm_dataset = svm_dataset.append(predict_frame) ####SEBBE MÅSTE FIXA DETTA, DEN LATA LILLA ODÅGAN

    scaled = scale(predict_frame)


    # svm_valence.predict(scaled)[0]
    # print(svm_dataset)
    # print(scaled)

    prediction_dict["Valence"] = svm_valence.predict(scaled)[0]
    prediction_dict["Arousal"] = svm_arousal.predict(scaled)[0]


def load_models():
    global svm_arousal, svm_valence
    global svm_dataset
    svm_arousal = joblib.load("Server/ML/Models/SVM_Arousal_model_job.sav")
    svm_valence = joblib.load("Server/ML/Models/SVM_Valence_model_job.sav")
    svm_dataset = pd.read_csv("Server/ML/Models/SVM_dataset.csv")
    svm_dataset.drop('Unnamed: 0', axis=1, inplace=True)



# ------------------------------------------ Files ------------------------------------------ #
def save_df(df, path, save_as_ext = '.csv'):
    filename = 'output_data' + str(full_data_dict["time"])    # get last part of path

    # if settings_dict["Training"] == True:
    #     filename += "_"
    #     filename += training_dict["Name"]

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
        with pd.ExcelWriter(str(path + "/" + filename)) as writer:          # module odf needed
            df.to_excel(writer) 

    elif save_as_ext == '.xlsx':
        filename = filename + save_as_ext
        df.to_excel(str(path + "/" + filename))
    else:
        filename = filename + '.csv'
        df.to_csv(str(path + "/" + filename))


def read_settings(settings_path):
    global settings_dict
    
    with open(settings_path, "r") as wow:
        settings_dict = json.load(wow)


# ------------------------------------------ Threads ------------------------------------------ #
def start_threads():
    global full_df
    global thread_names
    thread_names = []
    threads = []

    print("tcp thread starts")
    tcp_thread = threading.Thread(target=tcp_communication, daemon=True)
    tcp_thread.start()
    threads.append(tcp_thread)
    thread_names.append("tcp_thread")

    if settings_dict["EEG"] == True:
        #start thread/-s needed for EEG
        print("EEG thread starts")
        eeg_thread = threading.Thread(target=start_eeg)
        eeg_thread.start()
        threads.append(eeg_thread)
        thread_names.append("eeg_thread")
    else:
        calibration_done["EEG"] = True

    if settings_dict["Eyetracker"] == True:
        #start thread/-s needed for Eye tracker
        print("Eye thread starts")
        eye_thread = threading.Thread(target=get_eye_tracker_data) # ALT. threading.Thread(target=get_eye_tracker_data, daemon=True)
        eye_thread.start()
        threads.append(eye_thread)
        thread_names.append("eye_thread")

        print("Heatmap thread starts")
        heatmap_thread = threading.Thread(target=start_heatmap)
        heatmap_thread.start()
        threads.append(heatmap_thread)
        thread_names.append("heatmap_thread")
    else:
        calibration_done["Eye tracker"] = True
    
    if settings_dict["E4"] == True:
        #start thread/-s needed for Empatica E4
        print("E4 thread starts")
        e4_thread = threading.Thread(target=get_e4_data)
        e4_thread.start()
        threads.append(e4_thread)
        thread_names.append("e4_thread")
    else:
        calibration_done["E4"] = True

    # dataframe thread - Update the dataframe
    print("Dataframe thread starts")
    df_thread = threading.Thread(target=update_dataframe(True), daemon=True)    # df_thread = threading.Thread(target=update_dataframe(True), daemon=True)  # ÄNDRA PARAMETER TILL TRUE FÖR MOCK DF
    df_thread.start()
    threads.append(df_thread)
    thread_names.append("df_thread")
    calibration_done["Dataframe"] = True

    return threads

""" Closes all running threads included in the list """
def join_threads(threads):
    # print(threads)
    i = 0
    for t in threads:
        try:
            t.join()
            print(f"{thread_names[i]}: {str(t)} is now closed")
            i += 1
        except:
            print(f"failed to join {t}")

# ------------------------------------------ Dashboard ------------------------------------------ # 
def start_heatmap():
    global full_df

    all_done = False                                                                     ######################
    while not all_done:
        if all(sensor_calibration == True for sensor_calibration in calibration_done.values()):
            all_done = True

    print("calibration done - starting the heatmap creation")
    image_cache = []
    start = time.time()
    print("\n\n", full_df["time"].iloc[-1])
    last_time = datetime.datetime.strptime(full_df["time"].iloc[-1], format)

    # Run whole session (maybe future instead of max_time just have bool that check if user extension is connected)
    while time.time() - start < max_time:
        # Save constantly the newest row (date) in the dataframe
        current_time = datetime.datetime.strptime(full_df["time"].iloc[-1], format)

        # Check if the newest row (date) is older than 30 seconds then take screen shot
        if current_time - last_time > datetime.timedelta(0,20):
            print("TAKE PICTURE")
            # If cache is larger than 4 => (120 second with 4 images has gone by) we should save and clear
            if len(image_cache) >= 3:
                # Append last image
                image_cache.append(dashboard.screenshot_img(full_df["time"].iloc[-1]))
                # Create gif from the 120 seconds gone by made up by 4 images 30 seconds apart
                dashboard.create_heatmap_gif(image_cache, full_df)
                # Clear cache to continue the next 2 minutes and forward the whole session...
                image_cache.clear()
                # # Update last time
                # image_cache.append(dashboard.screenshot_img(full_df["time"].iloc[-1]))
            else:
                # If 4 images (120 seconds gone by) is NOT done just add and continue
                image_cache.append(dashboard.screenshot_img(full_df["time"].iloc[-1]))
            last_time = datetime.datetime.strptime(full_df["time"].iloc[-1], format)
        # Sleep 1 second to match up with dataframe update and to reduce CPU usage
        time.sleep(1)

    # Creation of heatmap dashboard when the thread is about to join (maybe change this to use either flask or django)
    dashboard.create_heatmap_dashboard()


def make_dashboard():
    global full_df

    try:
        dashboard.create_dashboard(full_df)
    except:
        print("[ERROR] - dashboard failed")


# ------------------------------------------ Main ------------------------------------------ #
if __name__ == "__main__":
    # load settings from settings file
    try:
        read_settings(SETTINGS_PATH)
    except:
        print("settings filepath not found")

    # initiate global empty dataframe
    init_df()

    # load AI models
    #load_models()
    try:
        load_models()
    except:
        print("[ERROR] - could not load AI models")

    # start localy hosted server
    setup_server()
    
    # start all available hardware threads and return array of activated threads
    threads = start_threads()

    # stop main thread until everything is finished         ############# Remake to a bool check so that it isn't time relyable
    time.sleep(max_time+4)

    # closing all the active threads
    join_threads(threads)

    # Save dataframe to a path and with specified format
    save_format = settings_dict["FileFormat"]
    save_path = settings_dict["SaveLocation"]
    save_df(full_df, save_path, save_format)

    #print(full_df.columns)

    make_dashboard()
    
    exit()

