
## MEMES
# #(╯°□°)╯︵ ┻━┻ :^) ┬─┬ノ( º _ ºノ)
# (╯°Д°)╯︵/(.□ . \)
#HAHAHAHAHHA123
# ( ͡° ͜ʖ ͡°)
## THE VOICES
#Wake up
import os
import sys
import random
import datetime
import threading
import time
import socket
import websockets
import warnings
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

#  Local imports
from Hardware.EEG import EEG
from Hardware.Eyetracker.eyetracker import EyeTracker
from Hardware.E4 import E4_client
from ML import Pop_up
import Dashboard.dashboard as dashboard

# imports
import jinja2
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') 
from matplotlib import pyplot as plt
import asyncio
import json
import joblib

from matplotlib.backends.backend_pdf import PdfPages

from sklearn.preprocessing import scale


format = "%d-%m-%YT%H-%M-%S"


# global variables
# socket settings
HOST_IP = "127.0.0.1" #lokala IPN, localhost
PORT = 6969
time_dict = {}
eeg_data_dict = {}
eye_data_dict = {}
e4_data_dict = {}
full_data_dict = {}
full_df = pd.DataFrame(dtype='object')
session_on = False
server_on = False
bad_path = os.path.dirname(os.path.realpath(__file__)) + "/settings.json"  # f'{os.path.dirname(os.path.abspath(__file__))}/settings.json'
SETTINGS_PATH = bad_path.replace("\\", "/")  # f'{os.path.dirname(os.path.abspath(__file__))}/settings.json'
session_id = 0

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
    """
    Starts the server-side with a TCP socket.

    Creates a TCP socket using the IPv4 address family (AF_INET) and TCP stream type (SOCK_STREAM).
    Binds the socket to the specified host IP address and port number. Listens for incoming connections
    and then starts a TCP thread to handle incoming connections and communication.
    
    Returns:
        tcp_thread (Thread): The thread responsible for handling TCP communication.

    Notes:
        -   AF = Address Family (IPv4)
        -   Sock_stream = type (TCP)
        -   Creates TCP thread using function 'start_tcp_thread()'
    """
    global tcp_socket
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((HOST_IP, PORT))
    tcp_socket.listen()
    print(f"SERVER: Hosting on IP:{HOST_IP} and listening on port:{PORT}")
    tcp_thread = start_tcp_thread()
    return tcp_thread

# ------------------------------------------ WEBSOCKETS ------------------------------------------ #

async def websocket_handler(websocket, path):
    global full_df, session_on
    try:
        while session_on:
            message = await websocket.recv()
            if "get_df" in message:
                data = {
                    'title': 'test',
                    'excitement': full_df['Excitement'].tolist(),
                    'engagement': full_df['Engagement'].tolist(),
                    'long_excitement': full_df['Long term excitement'].tolist(),
                    'stress': full_df['Stress/Frustration'].tolist(),
                    'relaxation': full_df['Relaxation'].tolist(),
                    'interest': full_df['Interest/Affinity'].tolist(),
                    'focus': full_df['Focus'].tolist(),
                    'pulse': full_df['Pulse'].tolist(),
                    "gsr": full_df["Gsr"].tolist(),
                    "bvp": full_df["Bvp"].tolist()
                }
                data_json = json.dumps(data)
                await websocket.send(data_json)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

    await websocket.close()

async def websocket_server():
    global session_on
    # Start the WebSocket server
    server = await websockets.serve(websocket_handler, "", 6960)
    print("Server started")

    # Wait until the session is over or a termination signal is received
    while session_on:
        await asyncio.sleep(1)  # Adjust the sleep duration as needed

    server.close()
    await server.wait_closed()

def start_websocket_server():
    # Create and run the event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(websocket_server())
    finally:
        loop.close()

#handles the connection to the extension
def tcp_communication():
    """
    Handles TCP communication (connection) between the server and the extension.

    Waits for the extension to establish a connection with the server.
    Receives messages from the extension, processes them accordingly, and sends responses back if necessary.
    Handles commands such as "settings_update", "get_emotion", "toggle_session", "disconnect", "ping", and "getPulse".
    Manages the session state and performs actions based on the received commands.

    Raises:
        Exception: If any exception occurs during socket connection between server and extension (if extension is not connected) .
        Exception: If any exception occurs during socket recieving data (if extension is connected).
    
    Notes:
        -   The function keeps executing and checking for socket connection if not connected to extension.
        -   The function keeps executing and checking for recieved data if it's connected to the extension.
    """
    global session_on
    global tcp_socket
    global session_id
    tcp_socket.settimeout(15)
    
    extension_connected = False
    print("Tries to connect to extension")
    while not extension_connected:
        try:
            conn, client = tcp_socket.accept()
            extension_connected = True
            print(f"Connected to {client}")
        except:
            print("failed to connect to extension, trying again")

    # when starting a session this list keeps track of active threads
    session_threads = []

    # Commands
    while extension_connected:
        #if time.time() - start < 200:
        #   session_on = False

        try:
            recived_msg = conn.recv(1024).decode('utf-8')
        except:
            print("no message from extension")
        
        if "toggle_session" in recived_msg:
            session_on = not session_on
            # if session starts, start the threads. If session ends, close the threads
            print(f"Toggle session to: {session_on}")
            if session_on:
                init_df()
                session_threads = start_session_threads()
                session_id = datetime.datetime.strftime(datetime.datetime.now(), format)
                
            if not session_on:
                # Save dataframe to a path and with specified format
                save_format = settings_dict["FileFormat"]
                save_path = settings_dict["SaveLocation"]

                save_df(full_df, save_path, save_format)
                make_dashboard()
                join_threads(session_threads)

        if "disconnect" in recived_msg:
            extension_connected = False
            print(f"Disconnecting from: {client}")
            conn.close()
            break

        if "get_data" in recived_msg:
            data = {
                "TypeOfData":"Hardware",
                "Pulse": e4_data_dict["Pulse"],
                "Emotion": (prediction_dict["Arousal"],prediction_dict["Valence"])
                }
            data_json = json.dumps(data)
            conn.sendall(data_json.encode("utf-8"))

        if "settings_update" in recived_msg:
            read_settings(SETTINGS_PATH)
            settings_dict["Training"] = False
            print("settings updated")


        if  "Ping" in recived_msg:
            print("IN PING")
            data = {
                "TypeOfData":"Ping",
                "Ping": "Pong"  
                }
            data_json = json.dumps(data)
            conn.sendall(data_json.encode('utf-8'))
            print("Received a ping from the client & responded wth pong.")


# ------------------------------------------ EEG ------------------------------------------ #
async def import_EEG_data():
    """
    Establishes a connection to the EEG, and starts receiving data from it.
    
    This asynchronouos function starts recording EEG data by initializing the api and setting up the api object.
    The 'calibration_done' dictionary is updated to indicate that the EEG calibration is complete.
    It then enters a loop to wait until all sensor calibrations are done before starting gathering data.
    The EEG data is continuously updated. Finally, the EEG ends is session when 'session_on' flag is False.

    Returns:
        int: 0 if the cortex api setup fails.

    Raises:
        Exception: If any exception occurs during cortext setup
    
    Notes:
        -   The function keeps executing and updating the 'eeg_data_dict' while the 'session_on' flag is True.
    """
    global eeg_data_dict
    global calibration_done

    #try to connect
    cortex_api = EEG.EEG()
    await cortex_api.connect()
    try:
        await cortex_api.setup()
    except:
        print("[ERROR] - EEG setup")
        calibration_done["EEG"] = True
        return 0

    calibration_done["EEG"] = True

    all_done = False
    while not all_done:
        if all(sensor_calibration == True for sensor_calibration in calibration_done.values()):
            all_done = True
    
    #gets data
    while session_on:
        time.sleep(1)
        eeg_data_dict = await cortex_api.get_eeg_data()

    #end cortex session
    await cortex_api.end_session()


def start_eeg():
    """
    Starts the EEG recorder.

    This function executes the function 'import_EEG_data()' within an asyncio event loop. This
    function starts the process of importing EEG data.
    """
    asyncio.run(import_EEG_data())


# ------------------------------------------ EYE TRACKER ------------------------------------------ #
def get_eye_tracker_data():
    """
    Creates an EyeTracker object, establishes a connection to the Eye Tracker, and starts receiving data from it.
    
    Starts recording eye tracker data by initializing the 'eye_tracker' object and setting up the eye tracker.
    The 'calibration_done' dictionary is updated to indicate that the eye tracker calibration is complete.
    It then enters a loop to wait until all sensor calibrations are done before starting the recording.
    The eye data is continuously updated. Finally, the eye tracker recording is stopped.

    Notes:
        -   The function keeps executing and updating the 'eye_data_dict' while the 'session_on' flag is True.
    """
    global calibration_done
    global eye_data_dict
    global full_df
    global session_on


    eye_tracker = EyeTracker(1)
    calibration_enabled = settings_dict['EyeTrackerCalibration']
    setup_failed = False
    print(calibration_enabled)
    try:
        eye_tracker.setup(calibration_enabled=calibration_enabled)
    except:
        print("[ERROR] - Eye tracker setup failed")
        setup_failed = True
    print("setup done")
    calibration_done["Eye tracker"] = True

    all_done = False
    while not all_done:
        if all(sensor_calibration == True for sensor_calibration in calibration_done.values()):
            all_done = True

    if not setup_failed:
        eye_tracker.start_recording(eye_data_dict, session_on)
        eye_tracker.stop()


# ------------------------------------------ E4 DATA TRACKER ------------------------------------------ #
def get_e4_data():
    """
    Creates an E4 connection and starts receiving data from the E4 device.

    This function establishes a connection with the E4 device and starts receiving Bvp, Gsr, and Hr data
    by initializing the 'e4_data_dict' and starting subscriptions. The calibration status is updated
    in the 'calibration_done' dictionary. It then enters a loop to continuously receive data, extracting
    the Hr, Bvp, and Gsr values. If the values are not empty, they are assigned to the corresponding keys
    in 'e4_data_dict'. The 'Pulse' value is converted to a float and checked against a threshold before
    assigning it.

    Notes:
        -   The function keeps executing while the 'session_on' flag is True.
    """
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

    while session_on:
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
    """
    Initalizes the dataframe and creates all columns, along with the dictionaries used for updating the dataframe.

    This function initializes the dataframe and dictionaries used for updating it. Global variables such as 'time_dict',
    'eye_data_dict', 'eeg_data_dict', 'e4_data_dict', 'prediction_dict', 'full_data_dict', 'full_df',
    and 'training_dict' are initialized. The 'full_df' is created as an empty DataFrame of object data type,
    and the dictionaries are initialized with default values. The function updates 'full_data_dict' with
    values from the dictionaries and appends it as the first row to the 'full_df' DataFrame.

    Note:
        -   The commented code related to the 'training_dict' is currently disabled.
    """
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

    if settings_dict["Training"] == True:
        training_dict = {
            "Name":"Jane Doe",
            "Age": None,
            "Initial pulse": None,
            "Arousal": None,
            "Valence": None,
            "Gender" : None,
            "Stress": 0
        }
        
        training_dict["Name"] = Pop_up.get_name() #samlar ursprungliga värden
        training_dict["Age"] = Pop_up.get_age()
        training_dict["Gender"] = Pop_up.get_gender()
        training_dict["Arousal"] = Pop_up.test_arousal() + 1
        training_dict["Valence"] = Pop_up.test_valence() + 1
        training_dict["Stress"] = Pop_up.get_stress()
        full_data_dict.update(training_dict)

    full_data_dict.update(time_dict)
    full_data_dict.update(eye_data_dict)
    full_data_dict.update(eeg_data_dict)
    full_data_dict.update(e4_data_dict)
    full_data_dict.update(prediction_dict)

    full_df = full_df.append(full_data_dict, ignore_index = True)

    
def update_dataframe():
    """
    Collects and updates data in the global dataframe.

    This function continuously collects data from various sources such as, eye_data_dict,
    time_dict, eeg_data_dict, e4_data_dict, and prediction_dict and updates the dataframe
    which is then appended to the global 'full_df' DataFrame.

    Raises:
        Exception: If any exception occurs while calling 'predict_series(full_data_dict)'
    
    Notes:
        -   The function keeps executing while the 'session_on' flag is True.
        -   The function sets the 'calibration_done' flag for the 'Dataframe' key to True.
        -   It retrieves mock data if the 'mock' flag is set to True instead of real data.
        -   The terminal is cleared using OS-specific commands ('cls' for Windows and 'clear' for other systems).
        -   If an exception occurs during the prediction process, a message is printed indicating the failure.
    """
    global full_df
    global session_on

    print_it = True
    mock = True

    calibration_done["Dataframe"] = True
    # all_done = True                                                                     ######################
    # while not all_done:
    #     if all(sensor_calibration == True for sensor_calibration in calibration_done.values()):
    #         all_done = True

    data_collection_timer = time.time()

    start = time.time()

    while session_on:
        delta = time.time() - start
        full_data_dict = {}
        time.sleep(1)

        if mock == True:
            mock_all_dicts()

        # Clear terminal
        # os.system('cls' if os.name == 'nt' else 'clear')                        ############################

        # time
        time_dict["time"] = datetime.datetime.now().strftime("%d-%m-%YT%H-%M-%S")
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
        training_time = 3

        if settings_dict["Training"] == True:
            if e4_data_dict["Pulse"] != 0 and training_dict["Initial pulse"] == None:
                training_dict["Initial pulse"] = e4_data_dict["Pulse"]
            if time.time() - data_collection_timer > training_time:
                training_dict["Arousal"] = Pop_up.test_arousal() + 1
                training_dict["Valence"] = Pop_up.test_valence() + 1
                training_dict["Stress"] = Pop_up.get_stress()

                data_collection_timer = time.time()
            full_data_dict.update(training_dict)
            training_dict["Valence"] = None
            training_dict["Arousal"] = None
            training_dict["Stress"] = 0

        

        try:
            predict_series(full_data_dict)
        except:
            print("prediction failed - prediction_dict not updated")
        # dataframe
        full_df = full_df.append(full_data_dict,ignore_index=True, sort=False)

        if print_it == True:
            print(f"{full_df}\n--------------------------------")                                     ###########################

def mock_all_dicts():
    """
    Modifies and updates global dictionaries with mock data.

    This function updates the global dictionaries eye_dat_dict, eeg_data_dict, e4_data_dict,
    and prediciton_dict with randomly generate mock data.
    """
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
    
    prediction_dict["Arousal"] = random.randrange(1, 5)
    prediction_dict["Valence"] = random.randrange(1, 5)

# ------------------------------------------ AI ------------------------------------------ #
def predict_series(full_data_dict):
    """
    Recieves the data from the full data dict, reformats it and changes the values in prediction
    dict based on the predictions of the trained AI model

    The function reads an SVM dataset from a CSV file, modifies certain fields in the data,
    and assigns it to a global variable. It then performs preprocessing steps such as dropping
    unnecessary fields, applying one-hot encoding, and scaling the dataset. Using an AI model,
    the function predicts values for 'Valence' and 'Arousal' based on the scaled dataset,
    storing the predictions in the 'prediction_dict' fields.

    Notes:
        -   The 'svm_dataset' is read from a CSV file named 'SVM_dataset.csv' and modified by dropping the 'Unnamed: 0' column.
        -   The scaled dataset is obtained using the 'scale' function.
        -   If the random number is greater than 50, the predicted 'Arousal' value comes from the AI model; otherwise, a default value is used.
    """
    global svm_dataset
    global eeg_predict_values
    global prediction_dict
    svm_dataset = pd.read_csv("Server/ML/Models/SVM_dataset.csv")
    svm_dataset.drop('Unnamed: 0', axis=1, inplace=True)
    full_data_dict["Gender"] = settings_dict["Gender"]
    full_data_dict["Age"] = settings_dict["Age"]
    eeg_predict_values = pd.Series(full_data_dict)

    drop_list = ["time", "x", "y", "Explorer", "Terminal", "Code", "Pulse", "Bvp", "Gsr", "Valence", "Arousal"]
    eeg_predict_values.drop(drop_list, inplace=True)
    
    predict_frame = pd.DataFrame(eeg_predict_values)
    predict_frame= predict_frame.transpose()

    predict_frame = pd.get_dummies(predict_frame, columns=["Gender"])
    # print(predict_frame)

    svm_dataset = svm_dataset.append(predict_frame)
    # print(svm_dataset)
    scaled = scale(svm_dataset)


    # svm_valence.predict(scaled)[0]
    # print(svm_dataset)
    # print(scaled)
    prediction_dict["Valence"] = svm_valence.predict([scaled[-1]])[0]
    if random.randrange(0, 100) > 50:
        prediction_dict["Arousal"] = svm_arousal.predict([scaled[-1]])[0]
    else:
        prediction_dict["Arousal"] = svm_arousal.predict([[ 0.,  1., -1.,  0., -1., -1., -1., -1.,  0.]])[0]



def load_models():
    """
    Loads the AI models and the dataset they were trained on

    The function loads the Support Vector Machine (SVW) models for arousal and valence prediciton,
    as well as the dataset used for training the models.

    Notes:
        -   The fucntion uses the 'joblib' library to load the SVM models from the specified file paths.
        -   The dataset is loaded using 'pd.read_csv' function.
        -   The 'svm_dataset' DataFrame has an 'Unnamed: 0' column, which is dropped for further processing.
        -   The loaded models and dataset are stored in the respective global variables: 'svm_arousal', 'svm_valence',
            and 'svm_dataset'.
    """
    global svm_arousal, svm_valence
    global svm_dataset
    svm_arousal = joblib.load("Server/ML/Models/SVM_Arousal_model_job.sav")
    svm_valence = joblib.load("Server/ML/Models/SVM_Valence_model_job.sav")
    svm_dataset = pd.read_csv("Server/ML/Models/SVM_dataset.csv")
    svm_dataset.drop('Unnamed: 0', axis=1, inplace=True)


# ------------------------------------------ Files ------------------------------------------ #
def save_df(df, path, save_as_ext = '.csv'):
    """
    Saves the dataframe

    The function saves the DataFrame to a file at the given path with the specified file extension.
    The file format options includes the following: [CSV, PDF, TSV, HTML, ODS, XLSX].

    Args:
        df (pandas.DataFrame): The DataFrame to be saved.
        path (str): The path where the file should be saved.
        save_as_ext (str, optional): The desired file extension. Defaults to '.csv'.
    
    Returns:
        int: 0 if the path does not exist.
    
    Notes:
        -   The 'filename' is detemined by appending the 'full_data_dict["time"]'
        -   The file formats supported are: CSV, PDF, TSV, HTML, ODS, and XLSX.
        -   The function uses the module matplotlib.pyplot as 'plt' to save as pdf
    """
    filename = 'output_data' + str(full_data_dict["time"])    # get last part of path

    if settings_dict["Training"] == True:
        filename += "_"
        filename += training_dict["Name"]

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

    print(f"Saved dataframe to: {filename}")

def read_settings(settings_path):
    """
    Reads the settings from the specified JSON file.

    Reads the contents of the JSON file located at the given settings_path
    (should point to settings.json). Updates the global variable
    settings_dict with the loaded settings.

    Args:
        settings_path (str): The path to the JSON file containing the settings.

    Raises:
        FileNotFoundError: If the specified JSON file is not found.
        JSONDecodeError: If the JSON file is invalid or cannot be parsed.

    Notes:
        - The JSON file must follow a valid JSON format.
        - The settings_dict global variable is updated with the loaded settings.
    """
    global settings_dict
    
    with open(settings_path, "r") as wow:
        settings_dict = json.load(wow)

    settings_dict["Training"] = False

# ------------------------------------------ Threads ------------------------------------------ #
def start_tcp_thread():
    """
    Starts a thread for the tcp communication

    This thread is on of the elementary functions which handles creating the TCP communication
    between the server and the extension. This further allows commands to be sent between the
    extension and the server.

    Returns:
        Thread: The thread handling the tcp communication
    
    Notes:
        -   This function uses the "tcp_communication()" function to use as a target for the thread
        -   This function uses the "threading" module to create threads
    """
    print("tcp thread starts")
    tcp_thread = threading.Thread(target=tcp_communication(), daemon=True)
    tcp_thread.start()
    return tcp_thread


def start_session_threads():
    """
    Starts threads that are active during a session

    This function is called if the session starts and is responsible to start all the active threads.
    It starts the threads required for EEG, Eye tracker, Emaptica E4, and updating the dataframe.

    Returns:
        list: A list of the started thread objects

    Examples:
        threads = start_session_threads()
        # Output: [eeg_thread, eye_thread, heatmap_thread, e4_thread, df_thread]
    
    Notes:
        -   The function checks the "settings_dict" dictionary to determine which threads to start based
            on the active devices.
        -   If a device is not active, the corresponding "calibration_done" flag is set to True.
        -   This function uses the "threading" module to create threads
    """
    global full_df
    threads = []

    if settings_dict["EEG"] == True:
        #start thread/-s needed for EEG
        print("EEG thread starts")
        eeg_thread = threading.Thread(target=start_eeg, daemon=True, name="Eeg thread")
        eeg_thread.start()
        threads.append(eeg_thread)
    else:
        calibration_done["EEG"] = True

    if settings_dict["Eyetracker"] == True:
        #start thread/-s needed for Eye tracker
        print("Eye thread starts")
        eye_thread = threading.Thread(target=get_eye_tracker_data, daemon=True, name="Eye thread") # ALT. threading.Thread(target=get_eye_tracker_data, daemon=True)
        eye_thread.start()
        threads.append(eye_thread)

        print("Heatmap thread starts")
        heatmap_thread = threading.Thread(target=start_heatmap, daemon=True, name="Heatmap thread")
        heatmap_thread.start()
        threads.append(heatmap_thread)
    else:
        calibration_done["Eye tracker"] = True
    
    if settings_dict["E4"] == True:
        #start thread/-s needed for Empatica E4
        print("E4 thread starts")
        e4_thread = threading.Thread(target=get_e4_data, daemon=True, name="E4 Thread")
        e4_thread.start()
        threads.append(e4_thread)
    else:
        calibration_done["E4"] = True

    # dataframe thread - Update the dataframe
    print("Dataframe thread starts")
    df_thread = threading.Thread(target=update_dataframe, daemon=True, name="Dataframe thread")    # df_thread = threading.Thread(target=update_dataframe(True), daemon=True)  # ÄNDRA PARAMETER TILL TRUE FÖR MOCK DF
    df_thread.start()
    threads.append(df_thread)
    calibration_done["Dataframe"] = True
    
    # 
    live_dashboard_thread = threading.Thread(target=start_websocket_server, daemon=True, name="live dashboard thread")
    live_dashboard_thread.start()
    threads.append(live_dashboard_thread)

    return threads


def join_threads(threads):
    """
    This function joins all the threads

    This function will take the inputed list of threads and joining them while printing out
    their names.

    Args:
        threads (list): Inputed list of threads

    Raises:
        Exception: If any exception occurs. Will print "failed to join {thread_name}"
    """
    print(f"all threads that's about to be joined {threads}")

    while threads:
        thread = threads.pop(0)
        if not thread.is_alive():
            print(f"{str(thread.name)} is already closed!")
        else:
            try:
                thread.join()
                print(f"{str(thread.name)} is now closed")
                print(f"Still running: {threads}\n")
            except:
                print(f"failed to join {thread.name}")

# ------------------------------------------ Dashboard ------------------------------------------ # 
def start_heatmap():
    """
    This is the heatmap thread

    This thread is used to continously take screenshots of the monitor in an interval
    and save them as a heatmap for the dashboard to use.

    Notes:
        -   This function uses the object "dashboard" which is an instande of the module
            "Dashboard.dashboard" located in {%projectPath}/Server/Dashboard/dashboard.py
        -   And uses the function screenshot_img(capture_name) and create_heatmap_gif(img_cache, df)
            from that instace.
    """
    global full_df
    global session_on

    all_done = False                                                                     ######################
    while not all_done:
        if all(sensor_calibration == True for sensor_calibration in calibration_done.values()):
            all_done = True

    print("calibration done - starting the heatmap creation")
    image_cache = []
    print("\n\n", full_df["time"].iloc[-1])
    last_time = datetime.datetime.strptime(full_df["time"].iloc[-1], format)

    while session_on:
        # Save constantly the newest row (date) in the dataframe
        current_time = datetime.datetime.strptime(full_df["time"].iloc[-1], format)

        # Check if the newest row (date) is older than 30 seconds then take screen shot
        if current_time - last_time > datetime.timedelta(0,30):
            print("TAKE PICTURE")
            # If cache is larger than 4 => (120 second with 4 images has gone by) we should save and clear
            if len(image_cache) >= 3:
                # Append last image
                image_cache.append(dashboard.screenshot_img(full_df["time"].iloc[-1]))
                # Create gif from the 120 seconds gone by made up by 4 images 30 seconds apart
                dashboard.create_heatmap_gif(image_cache, full_df, session_id)
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
    # dashboard.create_heatmap_dashboard()
    return 0


def make_dashboard():
    global session_id
    """
    This function is responsible to create the dashboard

    This function will create the combined dashboard from the current state of the
    dataframe. This will be rendered as a jinja2 templated located in the folder:
    {%projectPath}/Server/Dashboard/Saved_dashboard/combined_dashboard.html

    Raises:
        Exception: If any exception occurs. Will print "[ERROR] - dasboard failed"

    Notes:
        -   This function uses the object "dashboard" which is an instande of the module
            "Dashboard.dashboard" located in {%projectPath}/Server/Dashboard/dashboard.py
        -   And uses the function create_combined_dashboard(full_df) from that instace.
    """
    global full_df

    try:
        dashboard.create_combined_dashboard(full_df, session_id)
    except Exception as x:
        print("[ERROR] - dashboard failed", x)


# ------------------------------------------ Main ------------------------------------------ #
if __name__ == "__main__":
    """
    Main statement starting the server when run as a script

    This statement will be run through and initalizes all necessary components to run
    this project.
    """

    # load settings from settings file
    try:
        read_settings(SETTINGS_PATH)
        settings_dict["Training"] = False
    except:
        print("settings filepath not found")

    # initiate global empty dataframe
    init_df()
    try:
        load_models()
    except:
        print("[ERROR] - could not load AI models")

    # start localy hosted server
    tcp_thread = setup_server()
    threads = [tcp_thread]
    join_threads(threads)
    

    # Save dataframe to a path and with specified format
    # save_format = settings_dict["FileFormat"]
    # save_path = settings_dict["SaveLocation"]
    # save_df(full_df, save_path, save_format)

    #print(full_df.columns)

    # make_dashboard(False)
    
    exit()



# DOCUMENTATION FORMAT (GOOGLE STYLE)
"""
Brief description of the function.

More detailed description of the function's purpose, behavior,
and any specific details that are important to understand.

Args:
    param1 (type): Description of param1.
    param2 (type): Description of param2.

Returns:
    type: Description of the return value(s).

Raises:
    ExceptionType: Description of the exception(s) raised, if any.

Examples:
    Provide examples demonstrating how to use the function.

Notes:
    Additional notes or important information about the function.
"""