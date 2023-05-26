import pandas as pd
import matplotlib.pyplot as plt
import glob

filepath = "filepath med namn"  # <-- Filepath here

def first_clean(df):
    """
    Performs the initial cleaning steps on the DataFrame.

    Sets the first value of each EEG column to the first non-zero observed value.
    Removes one of the duplicate rows at the beginning of the DataFrame.
    Removes all rows with empty 'Valence' and 'Arousal' values.

    Args:
        df (pandas.DataFrame): The DataFrame to be cleaned.

    Returns:
        pandas.DataFrame: The cleaned DataFrame.

    Notes:
        - The input DataFrame 'df' is not modified; a copy is created for cleaning.
        - The first non-zero observed value for each EEG column is assigned to the first row.
        - One of the duplicate rows at the beginning of the DataFrame is dropped.
        - Rows with empty 'Valence' and 'Arousal' values are dropped.
    """

    df_copy = df.copy(True)
    temp_df = df_copy.ne(0).idxmax().to_frame('pos').assign(val=lambda d: df_copy.lookup(d.pos, d.index))
    temp_df["val"]
    df_copy["Engagement"].iloc[0] = temp_df["val"]["Engagement"]
    df_copy["Excitement"].iloc[0] = temp_df["val"]["Excitement"]
    df_copy["Stress/Frustration"].iloc[0] = temp_df["val"]["Stress/Frustration"]
    df_copy["Relaxation"].iloc[0] = temp_df["val"]["Relaxation"]
    df_copy["Interest/Affinity"].iloc[0] = temp_df["val"]["Interest/Affinity"]
    df_copy["Focus"].iloc[0] = temp_df["val"]["Focus"]
    df_copy = df_copy.copy(True).drop(1)
    df_copy = df_copy.copy(True).dropna(subset=['Valence', 'Arousal'])
    return df_copy


#Reads all csv files in a folder an adds them to a list
csv_files = glob.glob('Training_output/*.csv')
df_list = []
for i in csv_files:
    temp_df = pd.read_csv(i)
    df_list.append(temp_df)

#Cleans the data for all rows in the dataframe
result_df = pd.concat([first_clean(df) for df in df_list], ignore_index=True)

#saves the cleaned dataframe
filename = filepath + '.csv'
result_df.to_csv(str(filename))