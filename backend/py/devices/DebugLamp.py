import devices.Device as Device
import devices.Lamp as Lamp

class DebugLamp(Device.Device, Lamp.Lamp):
    def __init__(self):
        super().__init__()
        self._hasRGB = True
        self._hasTemperature = True

    def load_device(self, jsonData: dict):