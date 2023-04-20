# imports
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

# read csv file to df
def read_data(filepath):
    data_df = pd.DataFrame()
    try:
        # loads data to dataframe
        data_df = pd.read_csv(filepath)
    except:
        print("file not found")
    return data_df

# filter out needed df colums for ML
def ML_dataframe(data):
    age = data.iloc[:,2]
    arousal = data.iloc[:,4]
    valence = data.iloc[:,5]
    eeg = data.iloc[:,13:20]

    data_frames = [age, arousal, valence, eeg]
    ml_data = pd.DataFrame()
    ml_data = pd.concat(data_frames, axis=1, join="inner")
    
    return ml_data

#   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #

def random_forest(data):
    regressor = RandomForestRegressor(n_estimators=100, random_state=0)
    # fit the regressor with the training set
    try:
        regressor.fit(data)
    except:
        print("Random forest failed")


def multilayer_perceptron(data):
    pass


def support_vector_machine(data):
    pass


def k_nearest_neighbors(data):
    pass




if __name__ == "__main__":
    # get the data and filter out necessary dataframe colums
    file_data = read_data("C:/Users/David/Documents/GitHub/EmoIDE_project/Server/Training_output/output_data_Emil.csv")
    ml_data = ML_dataframe(file_data)
    
    # run algorithms
    random_forest(ml_data)
    

