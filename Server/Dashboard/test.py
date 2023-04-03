import pandas as pd
import datetime
format = "%d/%m/%Y-%H:%M:%S"

import numpy as np
import matplotlib.pyplot as plt

full_df = pd.read_csv('Output/output_data.csv')


def get_eye_coordinates_in_time_range(start_time, end_time):
    range_mask = (full_df["time"] > start_time) & (full_df["time"] <= end_time)
    return full_df.loc[range_mask]

print(full_df.to_string())

time_before_moment = datetime.datetime.strptime("02/04/2023-01:11:36", format)
print(time_before_moment - datetime.timedelta(seconds=30))
x = get_eye_coordinates_in_time_range("02/04/2023-01:11:36", "02/04/2023-01:17:36")['x'].to_numpy()
y = get_eye_coordinates_in_time_range("02/04/2023-01:11:36", "02/04/2023-01:17:36")['y'].to_numpy()

print(x, y)

plt.hist2d(x * 300,y * 300, bins=[np.arange(0,400,5),np.arange(0,300,5)])
# plt.set_cmap('plasma_r')
# plt.set_cmap('gnuplot2_r')
plt.set_cmap('CMRmap_r')
plt.axis('off')
plt.show()