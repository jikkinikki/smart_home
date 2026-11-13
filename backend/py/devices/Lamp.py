class Lamp():

    def __init__(self):
        self._isOn = False
        self._hasRGB = False
        self._hasTemperature = False
        self.allow_auto_updates = True

    def set_allow_auto_updates(self, allow: bool):
        self.allow_auto_updates = allow

    # What can be changed on this lamp. Names match the PATCH /devices fields.
    def get_capabilities(self) -> list[str]:
        capabilities = ["power", "brightness"]

        if self._hasTemperature:
            capabilities.append("temperature")

        if self._hasRGB:
            capabilities.append("color")

        return capabilities

    def turn_on(self, nowait: bool = False):

        self.allow_auto_updates = False

        if self._isOn:
            return;

    def turn_off(self, nowait: bool = False):

        self.allow_auto_updates = False

        if not self._isOn:
            return;

    def toggle(self, nowait: bool = False):
        self.allow_auto_updates = False

    def set_brightness(self, brightness: int, nowait: bool = False):
        if brightness < 0 or brightness > 100:
            print("Brightness must be between 0 and 100. Brightness: ", brightness);
            return False;

        self.allow_auto_updates = False

        return True;

    def set_temperature(self, temperature: int, nowait: bool = False):

        if not self._hasTemperature:
            print("Device does not support temperature");
            return False;

        if temperature < 0 or temperature > 100:
            print("Temperature must be between 0 and 100. Temperature: ", temperature);
            return False;

        self.allow_auto_updates = False

        return True;

    def set_color(self, color: tuple[int, int, int], nowait: bool = False):
        if not self._hasRGB:
            print("Device does not support color");
            return False;

        if color[0] < 0 or color[0] > 255 or color[1] < 0 or color[1] > 255 or color[2] < 0 or color[2] > 255:
            print("Color must be between 0 and 255. Color: ", color);
            return False;

        self.allow_auto_updates = False

        return True;
