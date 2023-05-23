# Unit test module
import unittest

# Other required modules
import pandas as pd
import datetime

# Test modules
from Dashboard.dashboard import get_df_in_time_range

class TestEyetracker(unittest.TestCase):
    def __init__(self, methodName=None):
        super().__init__(methodName=methodName)
        # Additional initialization

        self.format = "%d-%m-%YT%H-%M-%S"
    
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

        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestEyetracker))
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestEEG))
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestE4))

        return test_suite

    def run(self):
        unittest.TextTestRunner().run(self.suite)

if __name__ == '__main__':
    TestSuite().run()