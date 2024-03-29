import time
import threading

from .tools import OpenGazeTracker


class GazePoint(threading.Thread):
    def __init__(self, calibration_enabled, ip='127.0.0.1', port=4242):
        threading.Thread.__init__(self, daemon=True)
        self.interrupted = threading.Lock()

        self.gaze_position = (None, None)
        try:
            self.open(ip, port, calibration_enabled)
            self.start()
            self.wait_until_running()
            print(self.start)
        except:
            raise Exception

    def get_gaze_position(self):
        return self.gaze_position

    def run(self):
        try:
            self.interrupted.acquire()
            while self.interrupted.locked():
                self.gaze_position = self.tracker.sample()
        except:
            print("Gazepoint failed in gazepoint.py - run()")

    def stop(self):
        self.interrupted.release()
        self.close()

    def open(self, ip, port, calibration_enabled):
        print('Setting Up Gaze Point device, this takes about 10 seconds')
        try:
            self.tracker = OpenGazeTracker(ip=ip, port=port)
            if calibration_enabled:
                print("CALIBRATING")
                self.tracker.calibrate()
            print("NOT CALIBRATING")
            self.tracker.enable_send_data(True)
        except:
            print("Gazepoint failed")
            raise Exception

    def close(self):
        try:
            print('Closing connection to Gaze Point device, this takes about 5 seconds')
            self.tracker.enable_send_data(False)
            self.tracker.close()
        except:
            print("[EROR] Gazepoint close")

    def __del__(self):
        self.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def wait_until_running(self, sleep_time=0.01):
        while not self.interrupted.locked():
            time.sleep(sleep_time)


if __name__ == '__main__':
    gazetracker = GazePoint()

    start = time.time()
    while time.time() - start < 5:
        print(gazetracker.get_gaze_position())
        time.sleep(0.1)

    gazetracker.stop()
