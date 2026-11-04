import devices.Device as Device
import devices.Lamp as Lamp
from zigbee_remote import SharedZigbeeRemote, rgb_to_xy

class InnrLamp(Device.Device, Lamp.Lamp):
    def __init__(self):
        super().__init__()

        self._isOn = False
        self._hasRGB = False
        self._hasTemperature = False
        self.transition = 4  # tenths of a second

    def load_device(self, jsonData: dict):

        super().load_device(jsonData)

        self._zigbeeData = jsonData
        info = jsonData.get("zigbee", {})

        self.ieee = jsonData["dev_id"]
        self.nwk = int(jsonData["address"], 16)
        self.endpoint = info.get("endpoint") or 1

        capabilities = info.get("capabilities", [])
        self._hasRGB = "color" in capabilities
        self._hasTemperature = "color_temperature" in capabilities
        self.mireds_min, self.mireds_max = info.get("color_temp_mireds") or (153, 500)

        # All Zigbee devices share one connection to the USB dongle
        self.zigbee = SharedZigbeeRemote.get()
        self._is_ready = True

    def _send(self, coro, nowait: bool):
        self.zigbee.run(coro, wait=not nowait)

    def turn_on(self, nowait: bool = False):
        self._send(self.zigbee.remote.lamp_on(self.nwk, self.endpoint), nowait)
        self._isOn = True

    def turn_off(self, nowait: bool = False):
        self._send(self.zigbee.remote.lamp_off(self.nwk, self.endpoint), nowait)
        self._isOn = False

    def toggle(self, nowait: bool = False):
        self._send(self.zigbee.remote.lamp_toggle(self.nwk, self.endpoint), nowait)
        self._isOn = not self._isOn

    def set_brightness(self, brightness: int, nowait: bool = False):

        if not super().set_brightness(brightness, nowait=nowait):
            return False

        level = round(brightness / 100 * 254)  # Zigbee level is 0-254
        self._send(self.zigbee.remote.lamp_level(self.nwk, self.endpoint, level, self.transition), nowait)

    def set_temperature(self, temperature: int, nowait: bool = False):

        if not super().set_temperature(temperature, nowait=nowait):
            return False

        # 0 = warmest, 100 = coolest (same as Tuya). Zigbee uses mireds: higher = warmer.
        mireds = round(self.mireds_max - (self.mireds_max - self.mireds_min) * temperature / 100)
        self._send(self.zigbee.remote.lamp_color_temp(self.nwk, self.endpoint, mireds, self.transition), nowait)

    def set_color(self, color: tuple[int, int, int], nowait: bool = False):

        if not super().set_color(color, nowait=nowait):
            return False

        x, y = rgb_to_xy(*color)
        self._send(self.zigbee.remote.lamp_xy(self.nwk, self.endpoint, x, y, self.transition), nowait)

    def status(self):
        return self.zigbee.run(self.zigbee.remote.lamp_state(self.nwk, self.endpoint))
