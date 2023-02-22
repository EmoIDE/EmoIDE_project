from .gazepoint import gazepoint
import time

class EyeTracker:
    def __init__(self, frequency):
        self.eye_tracker = None
        self.recording = False
        self.cache = {
            "x": int,
            "y": int
        }
        self.frequency = frequency

    def setup(self):
        # Initializes default values and start calibration for use, may take 10 seconds
        self.eye_tracker = gazepoint.GazePoint()
        # self.cache = {
        #     "x": -1,
        #     "y": -1
        # }

    def start_recording(self, dict):
        # Start recording data to cache
        self.recording = True
        while self.recording:
            self.store_to_cache(self.eye_tracker.get_gaze_position(), dict)
            time.sleep(self.frequency)

    def get_recording(self):
        # Return cache with most recent coordinate
        return self.cache

    def stop_recording(self):
        # Stop recording data and return most recent coordinate
        self.recording = False
        return self.get_recording()

    def store_to_cache(self, coordinate, dict):
        # Store given coordinate to cahce
        dict["x"] = coordinate[0]
        dict["y"] = coordinate[1]

    def stop(self):
        # Clear cache, stop eyetracker may take 5 seconds
        self.cache.clear()
        self.eye_tracker.stop()


if __name__ == "__main__":
    eyetracker = EyeTracker()
    eyetracker.setup()
    eyetracker.start_recording()
    time.sleep(10)
    print(eyetracker.get_recording())
    eyetracker.stop()