import threading
import time
from control.device_handler import DeviceHandler

class DeviceCommands:

    def __init__(self, device_handler):

        self.device_handler = device_handler

        self.ambient = False
        self.devices_selector = ""

        self.commands = [

            {
                "desc": "turn off",
                "func": lambda: self.turn_off_devices(self.get_devices(), False),
                "btn": "off",
            },
            {
                "desc": "turn on",
                "func": lambda: self.turn_on_devices(self.get_devices(), False),
                "btn": "on",
            },
            {
                "desc" : "switch power",
                "func": lambda: self.switch_power(self.get_devices(), False),
                "btn": "switch_power",
            },
            {
                "desc": "set brightness (number:brightness)",
                "func": lambda : self.set_lamps_brightness(None),
                "ai_func": lambda b: self.set_lamps_brightness(b),
            },
            {
                "desc": "set Color temperature (number:kelvin)",
                "func": lambda: self.set_lamps_temperature(),
            },
            {
                "desc": "toggle ambient",
                "func": lambda: (ambient := not ambient),
            },
            {
                "desc": "Morning routine",
                "func": lambda: self.morningRoutine(),
            }
        ]

    def set_lamps_RGB(self, color, noWaitResp, onlyRGB = False):
        """color: '#rrggbb' (what the web colour picker sends) or an (r, g, b) tuple.
        onlyRGB: turn off the lamps that can't show colours."""

        if isinstance(color, str):
            hex_color = color.lstrip("#")
            color = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

        for device in self.get_devices():
            if getattr(device, "_hasRGB", False):
                device.set_color(tuple(color), nowait=noWaitResp)

            elif onlyRGB:
                device.turn_off(nowait=noWaitResp)

    def set_lamps_brightness(self, brightness, noWaitResp):

        # If you get error that from setting brigtness then check if
        # you are changing color temperature of the lamp at the same time. DONT DO THAT.
        #Maybe same for RGB.

        # New note. Is probably that you need the noWaitResp to be False.

        for device in self.get_devices():
            device.set_brightness(brightness=brightness, nowait=noWaitResp)


    def switch_power(self, power, noWaitResp):
        for device in self.get_devices():
            device.turn_on(nowait=noWaitResp) if power == "on" else device.turn_off(nowait=noWaitResp)

    def set_lamps_temperature(self, temp, noWaitResp):
        
        for device in self.get_devices():
                device.set_temperature(temperature=temp, nowait=noWaitResp)

    def morningRoutine(self):
        
            self.turn_on_devices(True)
            self.set_lamps_brightness(65, True)
            self.set_lamps_temperature(10, True)
            self.assistant.speak("Good morning Oskar!")

    def turn_off_devices(self, noWaitResp):

        for device in self.get_devices():
            device.turn_off(nowait=noWaitResp)

    def turn_on_devices(self, noWaitResp):
        
        for device in self.get_devices():
            print(device)
            device.turn_on(nowait=noWaitResp)

    def set_brightness(self, b):

        if not b:
            b = input("set brightness: ")
        
        self.set_lamps_brightness(int(b), False)

    def multithread(self, func):
        background_thread = threading.Thread(target=func, daemon=True)
        background_thread.start()

        return background_thread
    
    def get_devices(self):
        return self.device_handler.getSelectedDevices(self.devices_selector)
    
    def set_device_selector(self, selector):
            self.devices_selector = selector
    
# -TEST CODE------------------------------------------------------------------------------------------------

if(__name__ == "__main__"):
    
    dh = DeviceHandler()
    dc = DeviceCommands(DeviceHandler())

    dc.set_device_selector("all")

    dc.turn_on_devices(False)

    while True:
        time.sleep(1)
        dc.turn_on_devices(False)
