import pandas as pd
import matplotlib.pyplot as plt
import glob

filepath = "filepath med namn"#Sätt din filepath med här

def first_clean(df):
    '''Sätter första värdet till första obeserverade värdet för alla eegn värden, tar bort en 
    av dubletterna vi får i början av varje dataframe och tar bort alla tomma valence och arousal rader'''
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


#Läser in alla dataframes från ett folder och lägger in dem i en lista
#Ändra "Training/" till rätt folder där alla csv filer är sparade MEN TA INTE BORT STJÄRNAN
csv_files = glob.glob('Training/*.csv')
df_list = []
for i in csv_files:
    temp_df = pd.read_csv(i)
    df_list.append(temp_df)

#Rensar datan i alla dataframes i dataframe_list    
result_df = pd.concat([first_clean(df) for df in df_list], ignore_index=True)

#sparar alla rensade dataframes
filename = filepath + '.csv'
result_df.to_csv(str(filename))