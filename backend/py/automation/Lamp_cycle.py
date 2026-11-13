import time
import control.device_handler as dh
import control.device_commands as dc
import math

class Lamp_cycle:

    def __init__(self, device_handler, devices_selector, device_commands):

        self.device_handler = device_handler
        self.device_commands = device_commands
        self.devices_selector = devices_selector

        self.time_range = ["11:00", "23:00"]
        self.brightness_range = [1, 99]
        self.temperature_range = [1, 90]

        self.state = ""

    def loop(self):
        while True:
            self.update()
            time.sleep(5)

    def update(self):
        
        devices = self.get_devices()
        dc = self.device_commands
        # now_to_hhmm = lambda unix: time.strftime("%H:%M", time.localtime(unix))
        
        # now to hours:minutes string. e.g. "12:00"
        now_hhmm = lambda unix: time.strftime("%H:%M", time.localtime(unix))
        # now_hhmm = "23:00"
        # print(now_hhmm)

        time_start = self.hh_mm_to_ss(self.time_range[0])
        time_end = self.hh_mm_to_ss(self.time_range[1])
        
        time_current = self.hh_mm_to_ss(now_hhmm(time.time()))
        # time_current = self.hh_mm_to_ss(now_hhmm)

        print("time_current: ", time_current)

        if time_start <= time_current <= time_end:

            if self.state != "on":
                dc.turn_on_devices(devices, noWaitResp=True)
                self.state = "on"

            current = (time_current - time_start) / (time_end - time_start)
            print("current_perc: ", current)
            # print("perc_from_middle: ", dist_from_middle)
            
            new_b = self.get_value_from_range(self.brightness_range, current, "curved")
            new_t = self.get_value_from_range(self.temperature_range, current, "curved")

            print("new_b: ", new_b, 0 <= new_b <= 100)
            print("new_t: ", new_t, 0 <= new_t <= 100)
            dc.set_lamps_brightness(new_b, devices, noWaitResp=False)
            time.sleep(5)
            dc.set_lamps_temperature(new_t, devices, noWaitResp=False)

        else:

            if self.state != "off":
                dc.turn_off_devices(devices, noWaitResp=True)
                self.state = "off"

        # for lamp in self.lamps:

    def get_devices(self):
        devices = self.device_handler.getSelectedDevices(self.devices_selector)
        return devices

    def get_value_from_range(self, range, perc, mode):

        if(mode == "curved"):
            print("perc constant:", perc)
            perc = perc * math.pi # half circle on sin goes 0 to 1
            print("perc radians:", perc)
            perc = math.sin(perc) # curve between 0 and 1 that peaks at 0.5
            print("perc curved:", perc)

        elif(mode == "linear"):
            perc = 1 - abs(perc - 0.5) * 2 # Distance from middle
        
        return int(range[0] + (range[1] - range[0]) * perc)

    def hh_mm_to_ss(self, hh_mm):
        return sum(x * int(t) for x, t in zip([3600, 60], hh_mm.split(":")))
    
if(__name__ == "__main__"):

    lc = Lamp_cycle(dh.DeviceHandler(), "all", dc.DeviceCommands())
    lc.loop()