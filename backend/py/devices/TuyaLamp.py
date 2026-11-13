import tinytuya
import devices.Device as Device
import devices.Lamp as Lamp

class TuyaLamp(Device.Device, Lamp.Lamp):
    def __init__(self, hasRGB: bool):
        super().__init__()

        self._hasRGB = hasRGB
        self._hasTemperature = True
        self.tuya_connection_timeout = 3

    def load_device(self, jsonData: dict):

        super().load_device(jsonData)

        self._tuyaData = jsonData

        self.tuyaDevice = tinytuya.BulbDevice(
            dev_id=jsonData["dev_id"],
            address=jsonData["address"],
            local_key=jsonData["local_key"],
            version=jsonData["version"],
            connection_timeout=self.tuya_connection_timeout,
            )

        self.tuyaDevice.set_socketPersistent(True)
        self._is_ready = True

    def turn_on(self, nowait: bool = False):
        super().turn_on(nowait=nowait)

        self.tuyaDevice.turn_on(nowait=nowait)

    def turn_off(self, nowait: bool = False):
        super().turn_off(nowait=nowait)

        self.tuyaDevice.turn_off(nowait=nowait)

    def set_brightness(self, brightness: int, nowait: bool = False):

        if not super().set_brightness(brightness, nowait=nowait):
            return False;

        self.tuyaDevice.set_brightness_percentage(brightness, nowait=nowait)

    def set_temperature(self, temperature: int, nowait: bool = False):

        if not super().set_temperature(temperature, nowait=nowait):
            return False;

        self.tuyaDevice.set_colourtemp_percentage(temperature, nowait=nowait)

    def set_color(self, color: tuple[int, int, int], nowait: bool = False):
        if not super().set_color(color, nowait=nowait):
            return False;

        self.tuyaDevice.set_colour(color[0], color[1], color[2], nowait=nowait)