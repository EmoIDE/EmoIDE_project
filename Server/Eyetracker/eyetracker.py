import gazepoint
import time
import threading
# Create a GazePoint Instance
# This will start a calibration procedure after a few seconds
# Make sure the user is ready and the device is set before runnign this line
gazetracker = gazepoint.GazePoint()

# Get the gaze position
# x and y and relative coordinate to the screen
# (0, 0) is the upper left corner
# (1, 1) is the lower rigth corner
x, y = gazetracker.get_gaze_position()

# You can query gaze position as fast as desired
# Here for 5 seconds at 10Hz
start = time.time()
while time.time() - start < 20:
    print(gazetracker.get_gaze_position())
    time.sleep(0.1)



# Once done think of stopping the gazetracker, 
# It closes the connection properly and can take a few seconds
gazetracker.stop()
