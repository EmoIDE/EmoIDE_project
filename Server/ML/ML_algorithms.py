# imports
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

def read_data(filepath):
    """
    Reads a CSV file and returns a DataFrame.

    Attempts to load the data from the specified CSV file into a DataFrame.
    If the file is not found, an empty DataFrame is returned.

    Args:
        filepath (str): The path to the CSV file.

    Returns:
        pandas.DataFrame: The DataFrame containing the loaded data. If the file is not found, an empty DataFrame is returned.

    Notes:
        - The CSV file should have a proper format compatible with pandas' `read_csv()` function.
        - If the file is not found or cannot be read, an empty DataFrame is returned.
    """
    data_df = pd.DataFrame()
    try:
        # loads data to dataframe
        data_df = pd.read_csv(filepath)
    except:
        print("file not found")
        return data_df

def ML_dataframe(data):
    """
    Filters out the required columns from the given DataFrame for Machine Learning.

    This function takes a DataFrame as input and extracts specific columns needed for machine learning analysis.
    The columns extracted include 'age', 'arousal', 'valence', and the EEG values from columns 13 to 19.

    Args:
        data (pandas.DataFrame): The DataFrame containing the data to be filtered.

    Returns:
        pandas.DataFrame: The filtered DataFrame containing the columns 'age', 'arousal', 'valence', and
        the EEG values from columns 13 to 19.

    Note:
        The input DataFrame should contain the necessary columns for filtering, otherwise an empty DataFrame
        will be returned.

    """
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
    """
    Applies the Random Forest algorithm to the given data.

    This function utilizes the Random Forest algorithm to perform regression analysis on the provided data.
    It creates a RandomForestRegressor object with 100 estimators and a random state of 0, and then fits the regressor
    with the given data.

    Args:
        data (array-like, shape (n_samples, n_features)): The input data for regression analysis.

    Raises:
        Exception: If an error occurs during the fitting process.

    Note:
        The data should be in the format of an array-like object with shape (n_samples, n_features).
    """
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
    """
    Reads data from a file, filters necessary columns, and applies machine learning algorithms.

    This function reads data from a file located at given path.
    It then filters out the necessary columns using the 'read_data' and 'ML_dataframe' functions, and stores the result in 'ml_data'.
    Finally, it applies the 'random_forest' algorithm to the 'ml_data' and prints the result.

    Note:
        The file path is hardcoded in the function and should be adjusted if the file is located elsewhere.
    """
    # get the data and filter out necessary dataframe colums
    file_data = read_data("C:/Users/David/Documents/GitHub/EmoIDE_project/Server/Training_output/output_data_Emil.csv")
    ml_data = ML_dataframe(file_data)
    print(ml_data)
    
    # run algorithms
    random_forest(ml_data)
    

