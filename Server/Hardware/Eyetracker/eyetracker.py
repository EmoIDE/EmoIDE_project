from .gazepoint import gazepoint
import time

class EyeTracker:
    """
    EyeTracker class representing an EyeTracker object that connects to the GazePoint Eyetracker and retrieves data.
    """

    def __init__(self, frequency):
        """
        Initializes an EyeTracker instance.

        Also initializes the locations of the different zones on the monitor.

        Args:
            frequency (int): The frequency at which gaze data is recorded.
        """
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

    def setup(self, calibration_enabled):
        """
        Initializes the eye tracker and performs calibration.

        Returns:
            None

        Raises:
            Exception: If there is an error setting up the eye tracker.

        Notes:
            -   The setup of the eyetracker object may take up to 100 seconds.
        """
        try:
            self.eye_tracker = gazepoint.GazePoint(calibration_enabled)
        except:
            raise Exception

    def check(self, value, value_range):
        """
        Checks if a value falls within a given range.

        Args:
            value (float): The value to check.
            value_range (tuple): The range to compare against (start, end).

        Returns:
            bool: True if the value falls within the range, False otherwise.

        Raises:
            Exception: If there is an error during the check.
        
        Examples:
            check(0.5, (0.2, 1.0))
            # Output: True
        """
        try:
            if value_range[0] <= value <= value_range[1]:
                return True
        except:
            print("[ERROR] gazepoint check")
        return False
    
    def get_zone_destribution(self):
        """
        Calculates the distribution of gaze zones.

        Take in the current count for each zones and creates a dictionary that sums up
        the destribution in percentages for each zone.

        Returns:
            dict: A dictionary containing the zone distribution.

        Notes:
            -   The zone distribution is calculated based on the counts of each zone relative to the total count.
        """
        zone_destribution = {}
        for zone in self.zones:
            if sum([z['count'] for z in self.zones]) != 0:
                zone_destribution[zone['zone']] = round(zone['count']/sum([z['count'] for z in self.zones]),2)*100

        return zone_destribution

    def start_recording(self, dict, session_status):
        """
        Starts recording gaze data to the cache.

        Constantly at a frequency call function 'store_to_cache()' with the current coordinates of the gaze
        and also direct the 'dict' argument reference to be updated.

        Args:
            dict (dict): A dictionary to store the recorded data.
            session_status (bool): Flag indicating if the recording session is active.

        Notes:
            -   The recorded gaze data is stored in the cache at a specified frequency.
        """

        while session_status:
            self.store_to_cache(self.eye_tracker.get_gaze_position(), dict)
            time.sleep(self.frequency)

    def get_recording(self):
        """
        Retrieves the recorded gaze data from the cache.

        Returns:
            dict: The recorded gaze data.

        Notes:
            The returned data is the most recent coordinate stored in the cache.
        """

        return self.cache

    def stop_recording(self):
        """
        Stops the recording and returns the recorded gaze data.

        Returns:
            dict: The recorded gaze data.

        Notes:
            This function also stops the recording process.
        """

        self.recording = False
        return self.get_recording()

    def store_to_cache(self, coordinate, dict):
        """
        Stores a given coordinate to the cache.

        This function update the dictionary 'dict' with the current coordinate. Also mark which zone
        the coordinate was located in and then update the zone destribution accordingly.

        Args:
            coordinate (tuple): The coordinate to store (x, y).
            dict (dict): The dictionary to store the coordinate.

        Raises:
            Exception: If any exception occurs during the rounding and sum of zone counts.
        """
        # Store given coordinate to cahce
        dict["x"] = coordinate[0]
        self.cache["x"].append(coordinate[0])

        dict["y"] = coordinate[1]
        self.cache["y"].append(coordinate[1])

        for zone in self.zones:
            if(self.check(coordinate[0],zone['x']) and self.check(coordinate[1],zone['y'])):
                zone['count'] += 1
                break

        for zone in self.zones:
            try:
                dict[zone['zone']] = round((zone['count']/sum([z['count'] for z in self.zones]))*100,2)
            except:
                continue

    def stop(self):
        """
        Clears the cache and stops the eye tracker.
        """

        self.cache.clear()
        self.eye_tracker.stop()