import pyvisa

class PowerMeter:

    def __init__(self,
                 rm = None, # Stands for resource manager, essential to pyvisa. A resource is the device id string
                 resource_id = None,
                 device = None,
                 powermeter_name = 'ThorlabsPM100D' # For now we use always the same powermeter but it could be different
                 ):

        self.rm = pyvisa.ResourceManager()
        self.resource_id = resource_id
        self.device = device
        self.powermeter_name = powermeter_name

    def connect(self):

        devices_available = self.rm.list_resources()
        print("Available devices:", devices_available)

        if self.resource_id:

            self.device = self.rm.open_resource(self.resource_name)
            print(f"Connected to device {self.powermeter_name} at {self.resource_name}")

        else:
            for dev in devices:
                if "USB" in dev:  # You could also check for PM100D using IDN
                    try:
                        candidate = self.rm.open_resource(dev)
                        idn = candidate.query("*IDN?")
                        if "PM100D" in idn:
                            self.device = candidate
                            print("Connected to:", idn.strip())
                            break
                    except Exception as e:
                        print(f"Could not connect to {dev}: {e}")

        if self.device is None:
            raise RuntimeError("Could not find PM100D power meter.")

        self.device.write("*CLS")  # Clear status
        self.device.write("*RST")  # Optional reset

    def get_power(self):
        if self.device is None:
            raise RuntimeError("Device not connected.")
        return float(self.device.query("MEAS:POW?"))

    def get_idn(self):
        if self.device is None:
            raise RuntimeError("Device not connected.")
        return self.device.query("*IDN?")

    def close(self):
        if self.device:
            self.device.close()
            self.device = None