# Unit test module
import unittest

# Other required modules
import pandas as pd
import datetime
from unittest.mock import patch, mock_open

# Test modules
# --- Dashboard ---
from Dashboard.dashboard import get_df_in_time_range
from Dashboard.dashboard import format
from Dashboard.dashboard import output_path
from Dashboard.dashboard import create_combined_dashboard
# --- Eye tracker ---
from Hardware.Eyetracker.eyetracker import EyeTracker
from Hardware.Eyetracker.gazepoint.gazepoint import GazePoint

class TestDashboard(unittest.TestCase):
    def __init__(self, methodName=None):
        super().__init__(methodName=methodName)
        # Additional initialization
        self.format = format
        self.output_path = output_path
    
    def test_data_filtering_by_time_range(self):
        # Arrange
        data = {
            "time": [
                datetime.datetime(2023, 1, 1).strftime(self.format),
                datetime.datetime(2023, 1, 2).strftime(self.format),
                datetime.datetime(2023, 1, 3).strftime(self.format),
                datetime.datetime(2023, 1, 4).strftime(self.format),
                datetime.datetime(2023, 1, 5).strftime(self.format)
            ],
            "value": [1, 2, 3, 4, 5]
        }
        df = pd.DataFrame(data)

        expected_result = pd.DataFrame({
            "time": [
                datetime.datetime(2023, 1, 2).strftime(self.format),
                datetime.datetime(2023, 1, 3).strftime(self.format),
                datetime.datetime(2023, 1, 4).strftime(self.format)
            ],
            "value": [2, 3, 4]
        })

        start_time = datetime.datetime(2023, 1, 2)
        end_time = datetime.datetime(2023, 1, 4)

        # Act
        result = get_df_in_time_range(start_time, end_time, df).reset_index(drop=True)
        expected_result = expected_result.reset_index(drop=True)  # Reset index to match result DataFrame

        # Assert
        pd.testing.assert_frame_equal(result, expected_result)

    # @patch('builtins.open', create=True)
    @patch('Dashboard.dashboard.open', new_callable=mock_open)
    def test_create_combined_dashboard(self, mock_open):
        # Prepare sample input data
        df = pd.DataFrame({
            'Excitement': [1, 2, 3],
            'Engagement': [4, 5, 6],
            'Long term excitement': [7, 8, 9],
            'Stress/Frustration': [10, 11, 12],
            'Relaxation': [13, 14, 15],
            'Interest/Affinity': [16, 17, 18],
            'Focus': [19, 20, 21],
            'Pulse': [22, 23, 24],
            'Gsr': [25, 26, 27],
            'Bvp': [28, 29, 30],
            'time': [31, 32, 33]
        })

        # Call the function
        create_combined_dashboard(df)

        # Assert that the file is not actually opened
        mock_open.assert_called_once_with(self.output_path + "/combined_dashboard.html", "w")
        handle = mock_open.return_value.__enter__.return_value

        # Assert that the write method is called with the expected HTML content
        handle.write.assert_called_once()
        written_html = handle.write.call_args[0][0]  # Get the HTML content passed to write

        # Assert the expected content in the HTML
        self.assertIn('<html lang="en">', written_html)
        self.assertIn('</html>', written_html)

class TestEyetracker(unittest.TestCase):
    def __init__(self, methodName=None):
        super().__init__(methodName=methodName)
        # Additional initialization
    
    @patch('Hardware.Eyetracker.eyetracker.gazepoint.GazePoint', autospec=True)
    def test_setup(self, mock_gazepoint):
        # Mock gazepoint module
        eye_tracker = EyeTracker(1, 10)
        eye_tracker.setup(calibration_enabled=True)
        
        mock_gazepoint.assert_called_once_with(True)

    @patch('Hardware.Eyetracker.eyetracker.gazepoint.GazePoint', autospec=True)
    def test_setup_failure(self, mock_gazepoint):
        # Configure the mock to raise an exception when GazePoint is instantiated
        mock_gazepoint.side_effect = Exception("Gazepoint setup failed")

        # Create an instance of EyeTracker
        eye_tracker = EyeTracker(1, 10)

        # Call the setup method and capture the exception
        with self.assertRaises(Exception) as context:
            eye_tracker.setup(calibration_enabled=True)

        # Check if the exception message matches the expected error message
        self.assertEqual(str(context.exception), "Gazepoint setup failed")

    def test_check_within_range(self):
        # Create an instance of EyeTracker
        eye_tracker = EyeTracker(1, 10)

        # Call the check method with a value within the range
        result = eye_tracker.check(0.5, (0.2, 1.0))

        # Assert that the result is True
        self.assertTrue(result)

    def test_check_outside_range(self):
        # Create an instance of EyeTracker
        eye_tracker = EyeTracker(1, 10)

        # Call the check method with a value outside the range
        result = eye_tracker.check(1.5, (0.2, 1.0))

        # Assert that the result is False
        self.assertFalse(result)

    def test_get_zone_destribution(self):
        # Create an instance of EyeTracker
        eye_tracker = EyeTracker(50, 10)

        # Set up mock data for zones
        eye_tracker.zones = [
            {'zone': 'A', 'count': 20},
            {'zone': 'B', 'count': 10},
            {'zone': 'C', 'count': 30}
        ]

        # Call the get_zone_destribution method
        result = eye_tracker.get_zone_destribution()

        # Define the expected zone distribution
        expected_result = {
            'A': round(33.33),
            'B': round(16.67),
            'C': round(50.0)
        }

        # Assert that the actual result matches the expected result
        self.assertEqual(result, expected_result)

class TestEEG(unittest.TestCase):
    def __init__(self, methodName=None):
        super().__init__(methodName=methodName)
        # Additional initialization

class TestE4(unittest.TestCase):
    def __init__(self, methodName=None):
        super().__init__(methodName=methodName)
        # Additional initialization

class TestSuite():
    def __init__(self):
        self.suite = self.setup_suite()

    def setup_suite(self):
        test_suite = unittest.TestSuite()

        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDashboard))
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestEyetracker))
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestEEG))
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestE4))

        return test_suite

    def run(self):
        unittest.TextTestRunner().run(self.suite)

if __name__ == '__main__':
    TestSuite().run()
