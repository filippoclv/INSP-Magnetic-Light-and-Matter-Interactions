from pylablib.devices import Thorlabs # pip install pylablib
from pyThorlabsPM100x.driver import ThorlabsPM100x

class MotorizedPolarizer:

    def __init__(self,
                 angle_waveplate,
                 initial_polarizer_angle,
                 minimum_power_angle = None,
                 maximum_power_angle = None,
                 angle_polarizer = None,
                 motor = None,
                 ):

        self.angle_waveplate = angle_waveplate
        self.initial_polarizer_angle = initial_polarizer_angle

        def connect():

            detected_devices_list = Thorlabs.list_kinesis_devices()
            print("Detected devices:", detected_devices_list)

            if not detected_devices_list:

                raise RuntimeError("No Thorlabs devices found.")

            self.motor = Thorlabs.KinesisMotor(detected_devices[0][0], scale='stage')
            self.motor.setup_velocity(max_velocity=20, scale='stage')