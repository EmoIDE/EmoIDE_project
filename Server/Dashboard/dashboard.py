import datetime
import pyautogui
import os
import io
import jinja2
import pandas as pd
import base64
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

def create_dashboard(df):
    """
    Generates a dashboard HTML file using a Jinja2 template.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data to populate the dashboard.

    Notes:
        -   The function assumes that the DataFrame contains specific columns, such as 'Excitement', 'Engagement',
            'Long term excitement', 'Stress/Frustration', 'Relaxation', 'Interest/Affinity', 'Focus', 'Pulse', 'Gsr',
            'Bvp', and 'time'.
        -   The function retrieves data from the DataFrame and organizes it into lists for different dashboard components.
        -   The data is then passed to a Jinja2 template to render the HTML dashboard.
        -   The rendered HTML is saved to a file named 'dashboard.html'.
    """

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


def create_combined_dashboard(df, session_id):
    """
    Generates a combined dashboard HTML file using a Jinja2 template.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data to populate the dashboard.

    Notes:
        -   The function assumes that the DataFrame contains specific columns, such as 'Excitement', 'Engagement',
            'Long term excitement', 'Stress/Frustration', 'Relaxation', 'Interest/Affinity', 'Focus', 'Pulse', 'Gsr',
            'Bvp', and 'time'.
        -   The function retrieves data from the DataFrame and organizes it into lists for different dashboard components.
        -   It also gathers information about image files in a specific directory.
        -   The data is then passed to a Jinja2 template to render the HTML dashboard.
        -   The rendered HTML is saved to a file named 'combined_dashboard.html'.
    """

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

    bad_path = os.path.dirname(os.path.realpath(__file__)) + "/Heatmaps/"              #f'{os.path.dirname(os.path.abspath(__file__))}/Heatmaps/'     # bad_path = os.path.dirname(os.path.realpath(__file__)) + "/settings.json" 
    dirpath = bad_path.replace("\\", "/")
    staples = [f for f in os.listdir(dirpath) if os.path.isdir(os.path.join(dirpath, f))]
    text_list = []
    staple_images = []
    stress_list = [random.randint(50, 200) for f in range(0, len(staples))]
    for folder in staples:
        text_list.append(folder)
        folder_path = os.path.join(dirpath,folder)
        # timestamps=[]
        # for image in os.listdir(folder_path):
        #     image_path = os.path.join(folder_path, image)
        #     with open(image_path, "rb") as image2string:
        #         timestamps.append(base64.b64encode(image2string.read()).decode('utf-8'))
        # staple_images.append(timestamps)

        staple_images.append([os.path.join(folder_path, i).replace('\\', '/') for i in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, i)) and (i.endswith('.png'))])

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
        "bvp_list": bvp_list,
        'folder_staples': staples,
        'image_list': staple_images,
        'stress_list': stress_list,
        'text_list': text_list,
    }
    try:
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(output_path))
        template = env.get_template("combined_template.html")
        html = template.render(data)

        # Save the rendered HTML to a file
        filename = "/session/" + session_id + "/dashboard.html"
        filepath = str(output_path + filename)
        with open(filepath, "w") as f:
            f.write(html)
            print(f"Dashboard saved to: {filepath}")
    except Exception as e:
        print(e)



def get_df_in_time_range(start_time, end_time, df):
    """
    Retrieves a subset of a DataFrame based on a specified time range.

    Args:
        start_time (datetime.datetime): The start time of the desired time range.
        end_time (datetime.datetime): The end time of the desired time range.
        df (pandas.DataFrame): The DataFrame containing the data to filter.

    Returns:
        pandas.DataFrame: A subset of the original DataFrame that falls within the specified time range.

    Notes:
        -   The function assumes that the DataFrame has a column named "time" containing datetime values.
        -   The start_time and end_time are inclusive, meaning they are included in the filtered range.
        -   The time range is determined based on the values in the "time" column of the DataFrame.
        -   The function uses boolean masking to filter the DataFrame and retrieve rows within the specified range.
    """

    time_series = df["time"]
    start_time_series = datetime.datetime.strftime(start_time, format)
    end_time_series = datetime.datetime.strftime(end_time, format)
    range_mask = (time_series >= start_time_series) & (time_series <= end_time_series)
    return df.loc[range_mask]




def create_heatmap(moment_time, df):
    """
    Creates a heatmap based on data from a specific moment in time.

    Args:
        moment_time (str): The moment in time for which the heatmap is created, formatted according to the specified format.
        df (pandas.DataFrame): The DataFrame containing the data for generating the heatmap.

    Notes:
        - The function retrieves data from the DataFrame within a time range centered around the specified moment_time.
        - The time range is defined as the two minutes before and including the moment_time.
        - The x and y coordinates from the retrieved data are converted to pixel coordinates relative to the screen capture image.
        - A heatmap is created by plotting the converted coordinates over the corresponding screen capture image.
        - The heatmap image is saved as a PNG file in the "Heatmaps" directory relative to the current script's location, using the moment_time as the filename.
        - The density of the plotted points is represented using a color gradient defined by the 'coolwarm' colormap.
        - The resulting heatmap image is saved with a DPI of 300 and a tight bounding box.
    """
   
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
    """
    Captures a screenshot of the screen and saves it as an image file.

    Args:
        capture_name (str): The name of the captured screen image.

    Notes:
        - The function uses the pyautogui library to capture a screenshot of the screen.
        - The captured screenshot is saved as a PNG image file in the "Screencaptures" directory relative to the current script's location.
        - The captured screen image is named using the provided capture_name.
    """

    myScreenshot = pyautogui.screenshot()
    myScreenshot.save(f'{os.path.dirname(os.path.abspath(__file__))}/Screencaptures/{capture_name}.png')





# GIF VERSION (NOT FULLY FUNCTIONAL)
# def create_heatmap_gif(img_cache, df):
#     print(img_cache)
#     heatmap_cache = []

#     for screenshot in img_cache:
#         print(df)
#         print("----------------- CURRENT DATE: ", screenshot["date"])
#         before_moment = datetime.datetime.strptime(screenshot["date"], format) - datetime.timedelta(seconds=30)
#         print("----------------- 30 SECONDS BEFORE DATE: ", before_moment)

#         x = get_df_in_time_range(before_moment, datetime.datetime.strptime(screenshot["date"], format), df)['x'].to_numpy()
#         y = get_df_in_time_range(before_moment, datetime.datetime.strptime(screenshot["date"], format), df)['y'].to_numpy()

#         print("----------------- COORDINATES: ",x, y)
#         img = screenshot["img"]

#         img_arr = np.array(img)

#         # Convert x and y coordinates to pixel coordinates
#         x_pixel = x * img.width
#         y_pixel = y * img.height

#         xy = np.vstack([x,y])
#         density = gaussian_kde(xy)(xy)

#         # Create a heatmap over the image
#         plt.imshow(img_arr)
#         plt.scatter(x_pixel, y_pixel, s=100, c=density, cmap='coolwarm', alpha=0.25)

#         # Set axis limits and show the plot
#         plt.xlim([0, img.width])
#         plt.ylim([img.height, 0])
#         plt.axis('off')

#         fig = plt.gcf()
#         canvas = FigureCanvas(fig)
#         heatmap_cache.append(Image.frombytes('RGB', canvas.get_width_height(), canvas.tostring_rgb()))
#     # # Version 1.0
#     # frame_one = heatmap_cache[0]
#     # frame_one.save(f'{os.path.dirname(os.path.abspath(__file__))}/Heatmaps/{img_cache[-1]["date"]}.gif', format="GIF", append_images=heatmap_cache, save_all=True, duration=1000, loop=0)

#     # Version 2.0
#     with imageio.get_writer(f'{os.path.dirname(os.path.abspath(__file__))}/Heatmaps/{img_cache[-1]["date"]}.gif', mode='I') as writer:
#         for heatmap in heatmap_cache:
#             np_image = np.array(heatmap)
#             writer.append_date(np_image, duration=1000)
#     pass
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def create_heatmap_dashboard():
    """
    Creates a heatmap dashboard by rendering a Jinja2 template with heatmap data.

    Notes:
        - The function uses a Jinja2 template to generate an HTML dashboard with heatmaps.
        - Heatmap images are loaded from the "Heatmaps" directory relative to the current script's location.
        - Each subdirectory in the "Heatmaps" directory represents a group of heatmaps.
        - Heatmap images in each subdirectory are added to a carousel in the dashboard.
        - A stress level value is randomly generated for each group of heatmaps.
        - The generated HTML is saved to a file named "heatmap.html" in the specified output_path directory.
    """

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(output_path))
    template = env.get_template("heatmap_template.html")

    dirpath = f'{os.path.dirname(os.path.abspath(__file__))}/Heatmaps/'

    folders = [f for f in os.listdir(dirpath) if os.path.isdir(os.path.join(dirpath, f))]
    folder_carousel = []
    for folder in folders:
        folder_path = os.path.join(dirpath, folder)
        images = [os.path.join(folder_path, i) for i in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, i)) and (i.endswith('.png'))]
        carousel_html = '<div class="carousel">'
        for image in images:
            carousel_html += f'<img src="{os.path.join(folder, image)}">'
        carousel_html += '</div>'
        stress_level = random.randint(60, 250)

        folder_carousel.append((folder, carousel_html, stress_level))
    # Render the data in the Jinja2 template
    html = template.render({'folder_carousels': folder_carousel})

    # Save the rendered HTML to a file
    filename = "/heatmap.html"
    with open(str(output_path+  filename), "w") as f:
        f.write(html)

    # # Or any other template html service, the image carousel is done, just need a way to display it
    # return render(request, 'Saved_dashboards/heatmap_dashboard.html', {'folder_carousels': folder_carousel})

def create_heatmap_gif(img_cache, df, session_id):
    """
    Creates heatmaps for a series of images based on the provided data.

    Args:
        img_cache (list): A list of dictionaries containing image information.
        df (DataFrame): The DataFrame containing the data for generating heatmaps.

    Raises:
        FileExistsError: If directory already exists.

    Notes:
        - The function creates heatmaps for each image in the img_cache list.
        - The heatmaps are created based on the x and y coordinates stored in the df DataFrame.
        - Heatmap images are saved in the "Heatmaps" directory relative to the current script's location.
        - A subdirectory is created in the "Heatmaps" directory using the capture date as its name.
        - Heatmaps are saved as PNG images with filenames based on the capture date.
        - If there is insufficient data to create a heatmap for an image, a warning message is printed, and the original image is saved without modification.
        - The progress of processing each image is printed as a percentage.
    """

    dirpath = f'{os.path.dirname(os.path.abspath(__file__))}/Saved_dashboards/{session_id}/images/{img_cache[0]["date"]}'

    try:
        os.mkdir(dirpath)
    except FileExistsError:
        print(f'{bcolors.FAIL}Directory{bcolors.ENDC} {bcolors.UNDERLINE}{dirpath}{bcolors.ENDC} already exists')
    else:
        print(f'{bcolors.OKGREEN}Directory{bcolors.ENDC} {bcolors.UNDERLINE}{dirpath}{bcolors.ENDC} successfully created')

        for i, screenshot in enumerate(img_cache):
            before_moment = datetime.datetime.strptime(screenshot["date"], format) - datetime.timedelta(seconds=20)

            x = get_df_in_time_range(before_moment, datetime.datetime.strptime(screenshot["date"], format), df)['x'].to_numpy()
            y = get_df_in_time_range(before_moment, datetime.datetime.strptime(screenshot["date"], format), df)['y'].to_numpy()

            if len(x) <= 5 or len(y) <= 5:
                print(f'{bcolors.WARNING}Image{bcolors.ENDC} {bcolors.UNDERLINE}{dirpath + "/" + screenshot["date"] + ".png"}{bcolors.ENDC} not enough data to create heatmap')

                screenshot["img"].save(dirpath + "/" + screenshot["date"] + ".png")
            else:
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

                plt.savefig(dirpath + "/" + screenshot["date"] + ".png", dpi=300, format='png', bbox_inches='tight')

            print(f'Finished processing {bcolors.OKGREEN}{int(((i + 1) / len(img_cache)) * 100)}{bcolors.ENDC} % of all images')



def screenshot_img(capture_name):
    """
    Captures a screenshot and returns information about the capture.

    Args:
        capture_name (str): The name of the capture.

    Returns:
        dict: A dictionary containing the following information:
            - "date": The capture name.
            - "name": The absolute path to the captured image file.
            - "img": The captured screenshot image.

    Notes:
        - The capture name is used as the value for the "date" key in the returned dictionary.
        - The captured image file is saved in the "Screencaptures" directory relative to the current script's location.
        - The file name is generated by appending ".png" to the capture name.
        - The absolute path to the image file is stored as the value for the "name" key in the returned dictionary.
        - The captured screenshot image is stored as the value for the "img" key in the returned dictionary.
    """

    return {"date": capture_name, "name": f'{os.path.dirname(os.path.abspath(__file__))}/Screencaptures/{capture_name}.png', "img": pyautogui.screenshot()}



if __name__ == '__main__':
    # # Works with fake data
    # heatmap_thread()

    # Create dashboard testing
    create_heatmap_dashboard()




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
