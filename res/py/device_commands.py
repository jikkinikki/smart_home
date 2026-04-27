import threading
import time
from device_handler import DeviceHandler

class DeviceCommands:

    def __init__(self):

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

    def set_lamps_RGB(self, r, g, b, devicesToUpdate, noWaitResp, onlyRGB):

        for device in devicesToUpdate:
            if device.customData["type"] == "lamp" and device.has_colour:
                device.set_colour(r, g, b, nowait=noWaitResp)
            
            elif onlyRGB:
                device.turn_off(nowait=noWaitResp)

    def set_lamps_brightness(self, brightness, devicesToUpdate, noWaitResp):

        # If you get error that from setting brigtness then check if
        # you are changing color temperature of the lamp at the same time. DONT DO THAT.
        #Maybe same for RGB.

        # New note. Is probably that you need the noWaitResp to be False.

        for device in devicesToUpdate:

            device.set_brightness(brightness=brightness, nowait=noWaitResp)

            # elif device.customData["type"] == "outlet":

            #     outlet_status = device.status()
            #     brightnessLimit = device.customData["brightness"]

            #     if brightness < brightnessLimit and outlet_status["dps"]["1"] is True:
            #         device.turn_off(nowait=noWaitResp)
            #     elif brightness >= brightnessLimit and outlet_status["dps"]["1"] is False:
            #         device.turn_on(nowait=noWaitResp)


    def switch_power(self, power, devicesToUpdate, noWaitResp):
        for device in devicesToUpdate:
            device.turn_on(nowait=noWaitResp) if power == "on" else device.turn_off(nowait=noWaitResp)

    def set_lamps_temperature(self, temp, devicesToUpdate, noWaitResp):
        
        for device in devicesToUpdate:
                device.set_temperature(temperature=temp, nowait=noWaitResp)

    def morningRoutine(self):
        
            self.turn_on_devices(self.get_devices(), True)
            self.set_lamps_brightness(65, self.get_devices(), True)
            self.set_lamps_temperature(10, self.get_devices(), True)
            self.assistant.speak("Good morning Oskar!")

    def turn_off_devices(self, devicesToUpdate, noWaitResp):

        for device in devicesToUpdate:
            device.turn_off(nowait=noWaitResp)

    def turn_on_devices(self, devicesToUpdate, noWaitResp):
        
        for device in devicesToUpdate:
            print(device)
            device.turn_on(nowait=noWaitResp)

    def set_brightness(self, b):

        if not b:
            b = input("set brightness: ")
        
        self.set_lamps_brightness(int(b), self.get_devices(), False)

    def multithread(self, func):
        background_thread = threading.Thread(target=func, daemon=True)
        background_thread.start()

        return background_thread
    
    def get_devices(self):
        return dh.getSelectedDevices(self.devices_selector)
    
    def set_device_selector(self, selector):
            self.devices_selector = selector
    
# -TEST CODE------------------------------------------------------------------------------------------------

if(__name__ == "__main__"):
    dc = DeviceCommands()
    dh = DeviceHandler()

    dc.set_device_selector("all")

    dc.turn_on_devices(dc.get_devices(), False)

    while True:
        time.sleep(1)
        dc.turn_on_devices(dc.get_devices(), False)
