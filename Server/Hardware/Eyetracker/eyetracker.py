from .gazepoint import gazepoint
import time

class EyeTracker:
    def __init__(self, frequency):
        self.eye_tracker = None
        self.recording = False
        self.cache = {
            "x": [],
            "y": []
        }
        
        self.frequency = frequency

        self.zones = [
            {'x': (0, 0.2), 'y': (0, 1), 'zone': "Explorer", 'count' : 0},
            {'x': (0.2, 1), 'y': (0, 0.8), 'zone': "Code", 'count' : 0},
            {'x': (0.2, 1), 'y': (0.8, 1), 'zone': "Terminal", 'count' : 0}
        ]

    def setup(self):
        # Initializes default values and start calibration for use, may take 10 seconds
        self.eye_tracker = gazepoint.GazePoint()
        return

    def check(self, value, value_range):
        if value_range[0] <= value <= value_range[1] and round(value,2)==value:
            return True
        return False
    
    def get_zone_destribution(self):
        zone_destribution = {}
        for zone in self.zones:
            zone_destribution[zone['zone']] = round(zone['count']/sum([z['count'] for z in self.zones]),2)*100

        return zone_destribution

    def start_recording(self, dict):
        # Start recording data to cache
        print("EYE TRACKER START RECORDING...")
        start = time.time()
        while time.time() - start < 10:
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
        self.cache["x"].append(coordinate[0])

        dict["y"] = coordinate[1]
        self.cache["y"].append(coordinate[1])
        
        for zone in self.zones:
            if(self.check(coordinate[0],zone['x']) and self.check(coordinate[1],zone['y'])):
                zone['count'] += 1
        

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