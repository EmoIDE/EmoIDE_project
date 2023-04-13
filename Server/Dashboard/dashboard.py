import datetime
import pyautogui
import os
import io
import jinja2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

from PIL import Image
format = "%d-%m-%YT%H-%M-%S"
output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Saved_dashboards'))

def create_dashboard(df):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(output_path))
    template = env.get_template("template.html")
    excitement_list = df['Excitement'].tolist()
    engagement_list = df['Engagement'].tolist()
    long_excitement_list = df['Long term excitement'].tolist()
    stress_list = df['Stress/Frustration'].tolist()
    relaxation_list = df['Relaxation'].tolist()
    interest_list = df['Interest/Affinity'].tolist()
    focus_list = df['Focus'].tolist()
    pulse_list = df['Pulse'].tolist()
    gsr_list = df["Gsr"].tolist()
    bvp_list = df["Bvp"].tolist()
    index_list = df.index.tolist()

    # Prepare the data to be rendered in the Jinja2 template
    data = {
        'title': 'test',
        'excitement_list': excitement_list,
        'index_list': index_list,
        'engagement_list': engagement_list,
        'long_excitement_list': long_excitement_list,
        'stress_list': stress_list,
        'relaxation_list': relaxation_list,
        'interest_list': interest_list,
        'focus_list': focus_list,
        'pulse_list': pulse_list,
        "gsr_list": gsr_list,
        "bvp_list": bvp_list
    }

    # Render the data in the Jinja2 template
    html = template.render(data)

    # Save the rendered HTML to a file
    filename = "/dashboard.html"
    with open(str(output_path+  filename), "w") as f:
        f.write(html)
    pass





def get_df_in_time_range(start_time, end_time, df):
    time_series = df["time"]
    start_time_series = datetime.datetime.strftime(start_time, format)
    end_time_series = datetime.datetime.strftime(end_time, format)
    range_mask = (time_series >= start_time_series) & (time_series <= end_time_series)
    return df.loc[range_mask]




def create_heatmap(moment_time, df):
    # Pseudo code
    before_moment = datetime.datetime.strptime(moment_time, format) - datetime.timedelta(minutes=2)

    x = get_df_in_time_range(before_moment, datetime.datetime.strptime(moment_time, format), df)['x'].to_numpy()
    y = get_df_in_time_range(before_moment, datetime.datetime.strptime(moment_time, format), df)['y'].to_numpy()

    img = Image.open(f'{os.path.dirname(os.path.abspath(__file__))}/Screencaptures/{moment_time}.png')

    img_arr = np.array(img)

    # Convert x and y coordinates to pixel coordinates
    x_pixel = x * img.width
    y_pixel = y * img.height

    xy = np.vstack([x,y])
    density = gaussian_kde(xy)(xy)

    # Create a heatmap over the image
    plt.imshow(img_arr)
    plt.scatter(x_pixel, y_pixel, s=100, c=density, cmap='coolwarm', alpha=0.25)

    # Set axis limits and show the plot
    plt.xlim([0, img.width])
    plt.ylim([img.height, 0])
    plt.axis('off')
    plt.savefig(f'{os.path.dirname(os.path.abspath(__file__))}/Heatmaps/{moment_time}.png', dpi=300, format='png', bbox_inches='tight')



    # # WORKING BUT NOT TRADITIONAL HEATMAP DESIGN
    # # Read in the image and convert to RGBA format
    # img = Image.open(f'{os.path.dirname(os.path.abspath(__file__))}/Screencaptures/04-04-2023T22-33-29.png')

    # img_arr = np.array(img)

    # # Generate some sample data
    # x = np.random.rand(100)
    # y = np.random.rand(100)

    # # Convert x and y coordinates to pixel coordinates
    # x_pixel = x * img.width
    # y_pixel = y * img.height

    # # Create a heatmap over the image
    # plt.imshow(img_arr)
    # plt.scatter(x_pixel, y_pixel, c='red', alpha=0.35)

    # # Set axis limits and show the plot
    # plt.xlim([0, img.width])
    # plt.ylim([img.height, 0])
    # plt.show()




def capture_screen(capture_name):
    myScreenshot = pyautogui.screenshot()
    myScreenshot.save(f'{os.path.dirname(os.path.abspath(__file__))}/Screencaptures/{capture_name}.png')
