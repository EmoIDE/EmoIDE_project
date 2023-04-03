import datetime
import pyautogui
import os
import io
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image


def create_dashboard():
    pass


def create_heatmap(moment_time):
    from Backend.main import get_eye_coordinates_in_time_range

    # Pseudo code
    before_moment = datetime.datetime.strptime(moment_time, format) - datetime.timedelta(minutes=2)

    x = get_eye_coordinates_in_time_range(before_moment, moment_time)['x'].to_numpy()
    y = get_eye_coordinates_in_time_range(before_moment, moment_time)['y'].to_numpy()


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





def capture_screen():
    myScreenshot = pyautogui.screenshot()
    myScreenshot.save(f'{os.path.dirname(os.path.abspath(__file__))}/Screencaptures/{datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")}.png')
