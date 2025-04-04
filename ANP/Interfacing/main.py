import powermeter_class as pm
import pyvisa

def list_connected_devices():

    rm = pyvisa.ResourceManager()
    devices_available = rm.list_resources()
    print("Available devices:", devices_available)

