import datetime
import pyautogui
import os
import io
import jinja2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
#new import imageio
import imageio
import time
from scipy.stats import gaussian_kde
import random

from PIL import Image
format = "%d-%m-%YT%H-%M-%S"
output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Saved_dashboards'))
image_cache = []

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


def capture_screen(capture_name):
    myScreenshot = pyautogui.screenshot()
    myScreenshot.save(f'{os.path.dirname(os.path.abspath(__file__))}/Screencaptures/{capture_name}.png')





def create_heatmap_gif(img_cache, df):
    print(img_cache)
    heatmap_cache = []

    for screenshot in img_cache:
        print(df)
        print("----------------- CURRENT DATE: ", screenshot["date"])
        before_moment = datetime.datetime.strptime(screenshot["date"], format) - datetime.timedelta(seconds=30)
        print("----------------- 30 SECONDS BEFORE DATE: ", before_moment)

        x = get_df_in_time_range(before_moment, datetime.datetime.strptime(screenshot["date"], format), df)['x'].to_numpy()
        y = get_df_in_time_range(before_moment, datetime.datetime.strptime(screenshot["date"], format), df)['y'].to_numpy()

        print("----------------- COORDINATES: ",x, y)
        img = screenshot["img"]

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

        fig = plt.gcf()
        canvas = FigureCanvas(fig)
        heatmap_cache.append(Image.frombytes('RGB', canvas.get_width_height(), canvas.tostring_rgb()))
    # # Version 1.0
    # frame_one = heatmap_cache[0]
    # frame_one.save(f'{os.path.dirname(os.path.abspath(__file__))}/Heatmaps/{img_cache[-1]["date"]}.gif', format="GIF", append_images=heatmap_cache, save_all=True, duration=1000, loop=0)

    # Version 2.0
    with imageio.get_writer(f'{os.path.dirname(os.path.abspath(__file__))}/Heatmaps/{img_cache[-1]["date"]}.gif', mode='I') as writer:
        for heatmap in heatmap_cache:
            np_image = np.array(heatmap)
            writer.append_date(np_image, duration=1000)
    pass


def screenshot_img(capture_name):
    return {"date": capture_name, "name": f'{os.path.dirname(os.path.abspath(__file__))}/Screencaptures/{capture_name}.png', "img": pyautogui.screenshot()}


# Version 2.0 that always record but after two minutes it saves it (gif) and mark it based on level of stress
def heatmap_thread():
    max_time = 60
    start = time.time()
    full_df = pd.DataFrame()
    start_2 = time.time()
    while time.time() - start_2 < 10:
        new_data = {"time": datetime.datetime.now().strftime("%d-%m-%YT%H-%M-%S"), "x": random.random(), "y": random.random()}
        full_df = full_df.append(new_data, ignore_index=True)
        print(full_df)
        time.sleep(1)

    # Get image and time right now
    last_time = datetime.datetime.strptime(full_df["time"].iloc[-1], format)
    print(image_cache)

    # Run whole session (maybe future instead of max_time just have bool that check if user extension is connected)
    while time.time() - start < max_time:
        new_data = {"time": datetime.datetime.now().strftime("%d-%m-%YT%H-%M-%S"), "x": random.random(), "y": random.random()}
        full_df = full_df.append(new_data, ignore_index=True)
        # Save constantly the newest row (date) in the dataframe
        current_time = datetime.datetime.strptime(full_df["time"].iloc[-1], format)
        print(full_df)

        # Check if the newest row (date) is older than 30 seconds then take screen shot
        if current_time - last_time > datetime.timedelta(0,8):
            print("TAKE PICTURE")
            # If cache is larger than 4 => (120 second with 4 images has gone by) we should save and clear
            if len(image_cache) >= 3:
                # Append last image
                image_cache.append(screenshot_img(full_df["time"].iloc[-1]))
                # Create gif from the 120 seconds gone by made up by 4 images 30 seconds apart
                create_heatmap_gif(image_cache, full_df)
                # Clear cache to continue the next 2 minutes and forward the whole session...
                image_cache.clear()

                # Update last time
                image_cache.append(screenshot_img(full_df["time"].iloc[-1]))
            else:
                # If 4 images (120 seconds gone by) is NOT done just add and continue
                image_cache.append(screenshot_img(full_df["time"].iloc[-1]))
            last_time = datetime.datetime.strptime(full_df["time"].iloc[-1], format)
        # Sleep 1 second to match up with dataframe update and to reduce CPU usage
        time.sleep(1)

heatmap_thread()


# # Version 1.0 that only create heatmaps when stressed (only record 2 minutes at a time)
# def heatmap_thread(full_df, max_time):
#     start = time.time()
#     last_time = datetime.datetime.strftime(full_df["time"].iloc[-1], format)
#     image_cache.append(screenshot_img(full_df["time"].iloc[-1]))

#     while time.time() - start < max_time:
#         current_time = datetime.datetime.strftime(full_df["time"].iloc[-1], format)

#         if current_time - last_time > datetime.timedelta(0,30):
#             if len(image_cache) >= 4:
#                 image_cache.append(screenshot_img(full_df["time"].iloc[-1]))
#                 image_cache.pop(0)
#             else:
#                 image_cache.append(screenshot_img(full_df["time"].iloc[-1]))
