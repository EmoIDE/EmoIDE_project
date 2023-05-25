# Unit test module
import unittest

# Other required modules
import pandas as pd
import datetime
from unittest.mock import patch, mock_open, call, MagicMock

# Test modules
# --- Dashboard ---
from Dashboard.dashboard import get_df_in_time_range
from Dashboard.dashboard import format
from Dashboard.dashboard import output_path
from Dashboard.dashboard import create_combined_dashboard
# --- Eye tracker ---
from Hardware.Eyetracker.eyetracker import EyeTracker
from Hardware.Eyetracker.gazepoint.gazepoint import GazePoint
# --- EEG ---
from Hardware.EEG.EEG import EEG
# --- E4 ---
from Hardware.E4.E4_client import E4

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

    @patch('Dashboard.dashboard.open', new_callable=mock_open)
    @patch('Dashboard.dashboard.os.listdir')
    @patch('Dashboard.dashboard.os.path.isdir', return_value=True)  # Mock os.path.isdir() to always return True
    @patch('Dashboard.dashboard.get_df_in_time_range')  # Mock get_df_in_time_range() function
    def test_create_combined_dashboard(self, mock_get_df, mock_isdir, mock_listdir, mock_open):
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
        session_id = datetime.datetime.strftime(datetime.datetime.now(), format)

        # Mock the return value of os.listdir() to contain directories with correct format
        mock_listdir.return_value = [
            '23-05-2023T15-53-45',
            '24-05-2023T16-54-46',
            '25-05-2023T17-55-47'
        ]

        # Mock the return values of get_df_in_time_range() function
        mock_get_df.return_value = pd.DataFrame({
            'Valence': [0.8, 0.7, 0.6],
            'Arousal': [0.5, 0.4, 0.3]
        })

        # Call the function
        create_combined_dashboard(df, session_id)

        # Assert that the file is not actually opened
        mock_open.assert_called_once_with(f"{self.output_path}/session/{session_id}/dashboard.html", "w")
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
        eye_tracker = EyeTracker(1)
        eye_tracker.setup(calibration_enabled=True)
        
        mock_gazepoint.assert_called_once_with(True)

    @patch('Hardware.Eyetracker.eyetracker.gazepoint.GazePoint', autospec=True)
    def test_setup_failure(self, mock_gazepoint):
        # Configure the mock to raise an exception when GazePoint is instantiated
        mock_gazepoint.side_effect = Exception("Gazepoint setup failed")

        # Create an instance of EyeTracker
        eye_tracker = EyeTracker(1)

        # Call the setup method and capture the exception if raised
        with self.assertRaises(Exception) as context:
            eye_tracker.setup(calibration_enabled=True)

    def test_check_within_range(self):
        # Create an instance of EyeTracker
        eye_tracker = EyeTracker(1)

        # Call the check method with a value within the range
        result = eye_tracker.check(0.5, (0.2, 1.0))

        # Assert that the result is True
        self.assertTrue(result)

    def test_check_outside_range(self):
        # Create an instance of EyeTracker
        eye_tracker = EyeTracker(1)

        # Call the check method with a value outside the range
        result = eye_tracker.check(1.5, (0.2, 1.0))

        # Assert that the result is False
        self.assertFalse(result)

    def test_get_zone_destribution(self):
        # Create an instance of EyeTracker
        eye_tracker = EyeTracker(50)

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

# class TestEEG(unittest.TestCase):
#     def __init__(self, methodName=None):
#         super().__init__(methodName=methodName)
#         # Additional initialization
    
#     @patch('Hardware.EEG.EEG.websockets.connect')
#     async def test_get_eeg_data(self, mock_connect):
#         eeg = EEG()

#         fake_data = '{"met": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]}'
#         mock_recv = AsyncMock(return_value=fake_data)
#         mock_cortex = AsyncMock()
#         mock_cortex.recv = mock_recv
#         mock_connect.return_value = mock_cortex

#         await eeg.setup()

#         result = await eeg.get_eeg_data()
#         print(result)
#         expected_result = {
#             "Engagement": 1,
#             "Excitement": 3,
#             "Long term excitement": 4,
#             "Stress/Frustration": 6,
#             "Relaxation": 8,
#             "Interest/Affinity": 10,
#             "Focus": 12
#         }
#         self.assertEqual(result, expected_result)

#     @patch('websockets.connect', autospec=True)
#     def test_setup_success(self, mock_connect):
#         # CHeck if EEG tries to connect to socket url
#         with patch('builtins.print'):
#             eeg = EEG()
#             asyncio.run(eeg.connect())

#         mock_connect.assert_called_once_with("wss://localhost:6868")

#     def test_setup_failure(self):
#         pass

#     async def test_get_headset_id(self):
#         # Create a mock connection object
#         mock_connection = MagicMock()

#         # Create a mock message response
#         mock_response = {
#             "result": [
#                 {"id": "mock_headset_id"}
#             ]
#         }
#         mock_message = json.dumps(mock_response)

#         # Patch the send and recv methods to return the mock response
#         with patch.object(mock_connection, 'send') as mock_send, \
#                 patch.object(mock_connection, 'recv') as mock_recv:
#             # Set the return value of the mock_recv method
#             mock_recv.return_value = mock_message

#             # Replace self.cortex with the mock connection
#             self.cortex = mock_connection

#             # Call the function being tested
#             await self.get_headset_id()

#             # Assertions
#             mock_send.assert_called_once_with(json.dumps({
#                 "id": self.QUERY_HEADSET_ID,
#                 "jsonrpc": "2.0",
#                 "method": "queryHeadsets"
#             }))
#             mock_recv.assert_called_once()
#             print("AHHHHHHHHHHHHHHHh")
#             print(self.headset_id)
#             self.assertEqual(self.headset_id, "mock_headset_id")

class TestE4(unittest.TestCase):
    def __init__(self, methodName=None):
        super().__init__(methodName=methodName)
        # Additional initialization
        self.e4 = E4("localhost", 1234)

    @patch("socket.socket")
    @patch("socket.socket.connect")
    @patch("socket.socket.send")
    @patch("socket.socket.recv")
    def test_e4_ss_connect(self, mock_recv, mock_send, mock_connect, mock_socket):
        mock_socket.return_value = mock_socket
        mock_socket.recv.side_effect = [b"devices: Device1, Device2", b"success"]
        mock_socket.connect.return_value = None
        mock_socket.send.side_effect = [
            None,  # Call to device_discover_list
            None,  # Call to device_connect_btle
            None,  # Call to device_list
            None,  # Call to device_connect
            None,  # Call to device_subscribe bvp ON
            None   # Call to device_subscribe ibi ON
        ]

        self.e4.E4_SS_connect()

        # Did the E4 try to connect to the given ip:port from the _init_?
        mock_connect.assert_called_once_with(("localhost", 1234))
        # Did the E4 send method get called with specific arguments?
        mock_send.assert_has_calls([
            call(b"device_discover_list \n"),
            call(b"device_connect_btle 082FCD\n"),
            call(b"device_list \n"),
            call(b"device_connect 082FCD\n"),
        ], any_order=False)
        # Did the E4 recv get called at least once?
        self.assertTrue(mock_recv.called)
    
    @patch('Hardware.E4.E4_client.socket.socket')
    def test_start_subscriptions(self, mock_socket):
        # Setup 'socket.socket' mock
        mock_client_socket = MagicMock()
        mock_socket.return_value = mock_client_socket

        # Create instance and start subscription to our mock
        e4 = E4("127.0.0.1", 1234)
        e4.start_subscriptions()

        # Expected calls for the E4 to be sent for subscribing to our mock
        # And that all subscriptions is ON
        expected_calls = [
            call(b'device_subscribe bvp ON\n'),
            call(b'device_subscribe ibi ON\n'),
            call(b'device_subscribe gsr ON\n')
        ]

        # Asserts that the 'send' method of the mock 'socket.socket' has been called with the expected commands
        # You can see the mock value from print(mock_client_socket.send.mock_calls) which is equal to expected_calls
        mock_client_socket.send.assert_has_calls(expected_calls, any_order=False)

    @patch('Hardware.E4.E4_client.socket.socket')
    def test_receive_data(self, mock_socket):
        # Setup 'socket.socket' mock and return recv method with b'E4_Bvp 1680442024,64479 21,54169\r\n'
        mock_client_socket = MagicMock()
        mock_client_socket.recv.return_value = b'E4_Bvp 1680442024,64479 21,54169\r\n'
        mock_socket.return_value = mock_client_socket
        
        # Create instance and get received data
        e4 = E4("127.0.0.1", 1234)
        result = e4.recieve_data()

        # Assert that the result is as expected
        expected_result = ['', 'Bvp:21,54169', '']
        self.assertEqual(result, expected_result)

        # Assert that the client_socket.recv method was called
        self.assertGreaterEqual(mock_client_socket.recv.call_count, 1)

    @patch('Hardware.E4.E4_client.socket.socket')
    def test_e4_stop(self, mock_socket):
        # Mock the client_socket.send method and set up the expected response
        mock_client_socket = MagicMock()
        mock_socket.return_value = mock_client_socket
        # Call the e4_stop method
        e4 = E4("127.0.0.1", 1234)
        e4.e4_stop()

        # Assert that the client_socket.send and client_socket.recv methods were called for each request
        # And that all subscriptions is OFF and device disconnected
        expected_calls = [
            call(b'device_subscribe bvp OFF\n'),
            call(b'device_subscribe ibi OFF\n'),
            call(b'device_subscribe gsr OFF\n'),
            call(b'device_disconnect\n')
        ]
        # Asserts that the 'send' method of the mock 'socket.socket' has been called with the expected commands
        # You can see the mock value from print(mock_client_socket.send.mock_calls) which is equal to expected_calls
        mock_client_socket.send.assert_has_calls(expected_calls, any_order=False)

    def test_get_latest_values(self):
        # Create instance and get received data
        e4 = E4("127.0.0.1", 1234)
        arr = [
            'E4_Hr 1680442024,64479 68,56825\r\n',
            'E4_Bvp 5210038192,53792 -51,69904\r\n',
            'E4_Gsr 8520163812,12688 0,04481689\r\n'
        ]
        expected_result = ['Hr:68,56825', 'Bvp:-51,69904', 'Gsr:0,04481689']

        # Call the get_latest_values method
        result = e4.get_latest_values(arr)

        # Assert that the result is as expected
        self.assertEqual(result, expected_result)


class TestSuite():
    def __init__(self):
        self.suite = self.setup_suite()

    def setup_suite(self):
        test_suite = unittest.TestSuite()

        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDashboard))
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestEyetracker))
        # Difficulty to perform unit test due to asynchronous functions - unittest does not have built in suppport for async
        # test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestEEG))
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestE4))

        return test_suite

    def run(self):
        unittest.TextTestRunner().run(self.suite)

if __name__ == '__main__':
    TestSuite().run()
