import math
import time

class Indoor_Sun():
    """
    Makes the lamps follow the sun indoors: from sunrise they rise from dim and warm to
    bright and cool at the peak time, then go back down until sunset. Lamps are switched
    on at sunrise and off at sunset (only at those moments, so you can still switch them
    by hand).

        sun = Indoor_Sun(device_commands)
        sun.set_sun_period("07:30", "21:00", "13:00")   # sunrise, sunset, peak
        sun.set_sun_period(730, 2100, 1300)             # same, in military time
        multithread(sun.sun_loop)                       # like the other loops in main.py

    Without a peak time, the peak is halfway between sunrise and sunset.
    """

    def __init__(self, device_commands, sunrise = "10:00", sunset = "21:00", peak = "13:00"):

        self.device_commands = device_commands

        self.is_on = True
        self.turn_off_at_night = True

        self.brightness_range = [1, 100]   # percent: at sunrise/sunset -> at the peak
        self.temperature_range = [0, 70]   # percent of the lamp's colour-temperature range:
                                           # 0% = warmest, 100% = coolest

        self.update_interval = 30          # seconds between updates
        self.command_gap = 2               # seconds between brightness and temperature
                                           # (Tuya lamps can error when both are sent at once)

        self.sunrise = 0
        self.sunset = 0
        self.peak = 0
        self.set_sun_period(sunrise, sunset, peak)

        self._is_day = None
        self._last_brightness = None
        self._last_temperature = None

    # ---------- settings ----------

    def set_sun_period(self, sunrise, sunset, peak = None):
        """
        Times as "HH:MM" or military time (1000 = 10:00, 2130 = 21:30).
        sunrise: lamps turn on. sunset: lamps turn off.
        peak: brightest and coolest moment; must be between sunrise and sunset.
              None = halfway between sunrise and sunset.
        """
        sunrise = self.to_seconds(sunrise)
        sunset = self.to_seconds(sunset)
        day_length = (sunset - sunrise) % 86400

        if day_length == 0:
            raise ValueError("Sunrise and sunset can't be the same time")

        if peak is None:
            peak = (sunrise + day_length // 2) % 86400
        else:
            peak = self.to_seconds(peak)
            if not 0 < (peak - sunrise) % 86400 < day_length:
                raise ValueError("The peak time must be between sunrise and sunset")

        self.sunrise, self.sunset, self.peak = sunrise, sunset, peak
        self._is_day = None  # re-apply on/off on the next update

    def turn_on(self):
        self.is_on = True
        self._is_day = None
        self._last_brightness = None
        self._last_temperature = None

    def turn_off(self):
        self.is_on = False

    # ---------- loop ----------

    def sun_loop(self):

        while True:

            if self.is_on:
                try:
                    self.update()
                except Exception as e:
                    print(f"Indoor sun update failed: {e.__class__.__name__}: {e}")

            time.sleep(self.update_interval)

    def update(self, now = None):
        """Apply the sun for the time `now` (seconds since midnight, default: right now)."""

        if now is None:
            local = time.localtime()
            now = local.tm_hour * 3600 + local.tm_min * 60 + local.tm_sec

        is_day, brightness, temperature = self.get_sun_state(now)
        dc = self.device_commands

        if is_day != self._is_day:
            if is_day:
                dc.turn_on_devices(True)
            elif self.turn_off_at_night:
                dc.turn_off_devices(True)

            self._is_day = is_day
            self._last_brightness = None
            self._last_temperature = None

        if not is_day:
            return

        if brightness != self._last_brightness:
            dc.set_lamps_brightness(brightness, False)
            self._last_brightness = brightness
            time.sleep(self.command_gap)

        if temperature != self._last_temperature:
            dc.set_lamps_temperature(temperature, False)
            self._last_temperature = temperature

    # ---------- sun maths ----------

    def get_sun_state(self, now):
        """(is_day, brightness, temperature) for `now` in seconds since midnight."""

        height = self.get_sun_height(now)
        if height is None:
            return False, None, None

        brightness = self.value_in_range(self.brightness_range, height)
        temperature = self.value_in_range(self.temperature_range, height)

        return True, brightness, temperature

    def get_sun_height(self, now):
        """
        0.0 at sunrise -> 1.0 at the peak -> 0.0 at sunset, or None at night.
        Rising and setting each follow a smooth S-curve (half a cosine wave): gentle near
        sunrise/sunset and near the peak, steady change in between. They can have different
        lengths (e.g. a short morning and a long evening). Works across midnight too.
        """

        day_length = (self.sunset - self.sunrise) % 86400
        since_sunrise = (now - self.sunrise) % 86400
        rise_length = (self.peak - self.sunrise) % 86400

        if since_sunrise > day_length:
            return None

        if since_sunrise <= rise_length:
            progress = since_sunrise / rise_length
        else:
            progress = (day_length - since_sunrise) / (day_length - rise_length)

        return (1 - math.cos(progress * math.pi)) / 2

    @staticmethod
    def value_in_range(value_range, perc):
        return round(value_range[0] + (value_range[1] - value_range[0]) * perc)

    @staticmethod
    def to_seconds(value):
        """"HH:MM" or military time (int like 2130 or "2130") -> seconds since midnight."""

        if isinstance(value, str) and ":" in value:
            hours, minutes = value.split(":")
        else:
            military = int(value)
            hours, minutes = military // 100, military % 100

        hours, minutes = int(hours), int(minutes)
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            raise ValueError(f"Not a valid time: {value}")

        return hours * 3600 + minutes * 60

if (__name__ == "__main__"):
    # Run from the project root: python res/py/indoor_sun.py
    import device_commands as dc
    import device_handler as dh

    device_handler = dh.DeviceHandler()
    device_handler.wait_until_loaded()  # devices load in background threads

    device_commands = dc.DeviceCommands(device_handler)
    device_commands.set_device_selector("all")

    sun = Indoor_Sun(device_commands, "10:00", "21:00", "13:00")
    sun.sun_loop()  # loops forever