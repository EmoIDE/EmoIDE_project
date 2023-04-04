import datetime
import pyautogui
import os
import io
import jinja2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
format = "%d-%m-%YT%H-%M-%S"
output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Output'))

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


def create_heatmap(moment_time):
    from Server.main import get_eye_coordinates_in_time_range
    # from Backend.main import get_eye_coordinates_in_time_range

    # Pseudo code
    before_moment = datetime.datetime.strptime(moment_time, format) - datetime.timedelta(minutes=2)

    x = get_eye_coordinates_in_time_range(before_moment, datetime.datetime.strptime(moment_time, format))['x'].to_numpy()
    y = get_eye_coordinates_in_time_range(before_moment, datetime.datetime.strptime(moment_time, format))['y'].to_numpy()


    plt.hist2d(x,y, bins=[np.arange(0,400,5),np.arange(0,300,5)])
    # plt.set_cmap('plasma_r')
    # plt.set_cmap('gnuplot2_r')
    plt.set_cmap('CMRmap_r')
    plt.axis('off')


    heatmap_buf = io.BytesIO()
    plt.savefig(heatmap_buf, format='png', transparent=True)

    heatmap = Image.open(heatmap_buf)
    heatmap_w, heatmap_h = heatmap.size
    heatmap.putalpha(35)

    heatmap_f = heatmap.crop()
    newsize = (3440, 1440)
    heatmap_f = heatmap_f.resize(newsize)

    sceen_capture = Image.open(f'{os.path.dirname(os.path.abspath(__file__))}/Screencaptures/{moment_time}.png')
    sceen_capture_w, sceen_capture_h = sceen_capture.size
    offset = ((sceen_capture_w - heatmap_w) // 2, (sceen_capture_h - heatmap_h) // 2)

    # sceen_capture.paste(heatmap, offset, heatmap)
    sceen_capture.paste(heatmap_f, heatmap_f)
    sceen_capture.save(f'{os.path.dirname(os.path.abspath(__file__))}/Heatmaps/{moment_time}.png')





def capture_screen(capture_name):
    myScreenshot = pyautogui.screenshot()
    myScreenshot.save(f'{os.path.dirname(os.path.abspath(__file__))}/Screencaptures/{capture_name}.png')
